import base64
import re
from datetime import datetime, timezone
from github.GithubException import UnknownObjectException
from packaging.version import parse as parse_version, InvalidVersion

# Note that this implementation relies on the packaging library to correctly parse and compare semantic versions 
# from repository tags. You may need to add it to your project's dependencies (e.g., pip install packaging).

# Assuming config.py is in the same src directory and contains get_app_config()
# with the necessary keys as described in the requirements.
from src.config import Config

class Sanitizer:
    """
    Sanitizes raw repository data from a Git platform into the code.json format
    by applying a set of business rules.
    """

    # --- Define Exemption Codes as Constants ---
    EXEMPT_BY_LAW = "exemptByLaw"
    EXEMPT_BY_NATIONAL_SECURITY = "exemptByNationalSecurity"
    EXEMPT_BY_AGENCY_SYSTEM = "exemptByAgencySystem"
    EXEMPT_BY_MISSION_SYSTEM = "exemptByMissionSystem"
    EXEMPT_BY_CIO = "exemptByCIO"

    VALID_EXEMPTION_CODES = [
        EXEMPT_BY_LAW, EXEMPT_BY_NATIONAL_SECURITY, EXEMPT_BY_AGENCY_SYSTEM,
        EXEMPT_BY_MISSION_SYSTEM, EXEMPT_BY_CIO,
    ]

    # --- Define Non-Code Languages ---
    # Languages are compared in lowercase.
    NON_CODE_LANGUAGES = [
        'markdown', 'text', 'html', 'css', 'xml', 'yaml', 'json',
        'shell', 'batchfile', 'powershell', 'dockerfile', 'makefile', 'cmake',
        'tex', 'roff', 'csv', 'tsv'
    ]

    def __init__(self):
        """Initializes the Sanitizer with configuration and regex patterns."""
        self.config = Config().get_app_config()
        self.email_regex = re.compile(r'[\w.+-]+@cdc\.gov')
        # Case-insensitive regex to find "Key: Value" at the start of a line
        self.marker_regex_template = r'(?i)^\s*{}:\s*(.*)$'

    def _get_file_content(self, repo, file_path):
        """
        Fetches and decodes the content of a file from the repository.

        Args:
            repo: The PyGithub Repository object.
            file_path: The path to the file in the repository (e.g., 'README.md').

        Returns:
            The decoded file content as a string, or None if not found or on error.
        """
        try:
            content_item = repo.get_contents(file_path)
            return base64.b64decode(content_item.content).decode('utf-8', errors='ignore')
        except UnknownObjectException:
            return None  # File not found is a normal case
        except Exception as e:
            print(f"Error fetching '{file_path}' for {repo.full_name}: {e}")
            return None

    def _parse_marker(self, content, key):
        """
        Parses a text block for a specific "Key: Value" marker.

        Args:
            content: The text content to search within.
            key: The key to look for (e.g., 'Organization|Org').

        Returns:
            The stripped value if the marker is found, otherwise None.
        """
        if not content:
            return None
        regex = re.compile(self.marker_regex_template.format(key), re.MULTILINE)
        match = regex.search(content)
        return match.group(1).strip() if match else None

    def _infer_organization(self, repo, readme_content):
        """Infers the organization based on README markers and repository name."""
        # 1. README Marker (highest priority)
        org_from_readme = self._parse_marker(readme_content, 'Organization|Org')
        if org_from_readme:
            return org_from_readme

        # 2. Programmatic Check for known acronyms in repo name
        repo_name_lower = repo.name.lower()
        for acronym, full_name in self.config.get('ORG_ACRONYMS', {}).items():
            acronym_lower = acronym.lower()
            if f"{acronym_lower}-" in repo_name_lower or f"-{acronym_lower}" in repo_name_lower:
                return full_name

        # 3. Default to agency name
        return self.config.get('AGENCY_NAME', 'CDC')

    def _infer_contact_email(self, repo, readme_content, codeowners_content):
        """Infers the contact email based on visibility, README, and CODEOWNERS."""
        if repo.private:
            return self.config.get('PRIVATE_REPO_CONTACT_EMAIL', 'shareit@cdc.gov')

        # Public Repository Logic
        # 1. README Marker
        emails_from_marker_str = self._parse_marker(readme_content, 'Contact email')
        if emails_from_marker_str:
            emails = self.email_regex.findall(emails_from_marker_str)
            if emails:
                return ";".join(sorted(list(set(emails))))

        # 2. CODEOWNERS file
        if codeowners_content:
            emails = self.email_regex.findall(codeowners_content)
            if emails:
                return ";".join(sorted(list(set(emails))))

        # 3. Anywhere else in README
        if readme_content:
            emails = self.email_regex.findall(readme_content)
            if emails:
                return ";".join(sorted(list(set(emails))))

        # 4. Default
        return self.config.get('DEFAULT_CONTACT_EMAIL', 'cdcinfo@cdc.gov')

    def _infer_status(self, repo, readme_content):
        """Infers the repository status with a defined order of precedence."""
        # 1. Archived status from platform
        if repo.archived:
            return "archived"

        # 2. Status marker in README
        status_from_readme = self._parse_marker(readme_content, 'Status')
        if status_from_readme:
            return status_from_readme.lower()

        # 3. Inactive check (no modifications for over 2 years)
        now = datetime.now(timezone.utc)
        last_modified = repo.pushed_at.replace(tzinfo=timezone.utc)
        if (now - last_modified).days > 730:
            return "inactive"

        # 4. Default status
        return "development"

    def _infer_version(self, repo, readme_content):
        """Infers the version from tags or a README marker."""
        # 1. Scan tags for the latest valid semantic version
        latest_version = None
        tags = repo.get_tags()
        for tag in tags:
            try:
                # Remove common prefixes like 'v'
                version_str = tag.name.lstrip('vV')
                current_version = parse_version(version_str)
                if not current_version.is_prerelease:
                    if latest_version is None or current_version > latest_version:
                        latest_version = current_version
            except InvalidVersion:
                continue  # Ignore tags that are not valid versions

        if latest_version:
            return str(latest_version)

        # 2. Fallback to README marker
        version_from_readme = self._parse_marker(readme_content, 'Version')
        if version_from_readme:
            return version_from_readme

        # 3. Default
        return "N/A"

    def _infer_usage_and_url(self, repo, readme_content, languages):
        """Determines usageType, exemptionText, and repositoryURL based on a set of rules."""
        # --- Public Repositories ---
        if not repo.private:
            usage_type = "openSource" if repo.license else "governmentWideReuse"
            return usage_type, None, repo.html_url

        # --- Private or Internal Repositories ---
        # 1. Manual README Marker (highest priority)
        exemption_type_from_marker = self._parse_marker(readme_content, 'Exemption')
        if exemption_type_from_marker and exemption_type_from_marker in self.VALID_EXEMPTION_CODES:
            justification = self._parse_marker(readme_content, 'Exemption justification')
            url = self.config.get('EXEMPTED_NOTICE_PDF_URL')
            return exemption_type_from_marker, justification, url

        # 2. Non-Code Check
        # A repository with no detected languages is also considered non-code.
        if not languages or all(lang.lower() in self.NON_CODE_LANGUAGES for lang in languages if lang):
            usage_type = self.EXEMPT_BY_CIO
            justification = "Repository contains no code or only non-code assets like documentation and configuration."
            url = self.config.get('EXEMPTED_NOTICE_PDF_URL')
            return usage_type, justification, url

        # 3. Default for private/internal repos
        usage_type = "governmentWideReuse"
        url = self.config.get('INSTRUCTIONS_PDF_URL')
        return usage_type, None, url

    def get_repository_metadata(self, repo) -> dict:
        """
        Processes a single repository object and returns its sanitized metadata.

        Args:
            repo: A PyGithub Repository object.

        Returns:
            A dictionary containing the sanitized repository metadata, or None if
            the repository should be skipped (e.g., it's a fork).
        """
        if repo.fork:
            print(f"Skipping forked repository: {repo.full_name}")
            return None

        # Skip empty repositories to avoid errors when fetching contents.
        if repo.size == 0:
            print(f"Skipping empty repository: {repo.full_name}")
            return None

        try:
            # --- Fetch file contents once ---
            readme_content = self._get_file_content(repo, 'README.md')
            codeowners_content = self._get_file_content(repo, 'CODEOWNERS')

            # --- Fetch raw data and perform inferences ---
            languages = list(repo.get_languages().keys())
            usage_type, exemption_text, repository_url = self._infer_usage_and_url(repo, readme_content, languages)
            status = self._infer_status(repo, readme_content)
            organization = self._infer_organization(repo, readme_content)
            contact_email = self._infer_contact_email(repo, readme_content, codeowners_content)
            version = self._infer_version(repo, readme_content)

            # --- Assemble the final metadata object ---
            metadata = {
                "name": repo.name,
                "organization": organization,
                "description": repo.description or "",
                "version": version,
                "status": status,
                "vcs": "git",
                "homepageURL": repo.homepage or "",
                "repositoryURL": repository_url,
                "repositoryVisibility": "private" if repo.private else "public",
                "languages": languages,
                "tags": repo.get_topics(),
                "contact": {
                    "email": contact_email
                },
                "date": {
                    "created": repo.created_at.isoformat(),
                    "lastModified": repo.pushed_at.isoformat(),
                    "metadataLastUpdated": datetime.now(timezone.utc).isoformat()
                },
                "permissions": {
                    "usageType": usage_type,
                    "licenses": [{"name": repo.license.name}] if repo.license else []
                }
            }

            # Conditionally add optional fields
            if exemption_text:
                metadata["permissions"]["exemptionText"] = exemption_text

            if repo.private:
                metadata["privateID"] = f"github_{repo.id}"

            return metadata

        except Exception as e:
            print(f"Failed processing repository {repo.full_name}: {e}")
            import traceback
            traceback.print_exc()
            return None
