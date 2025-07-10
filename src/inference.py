import re

from datetime import datetime, timezone
from src.organization import Organization
from src.config import Config

from packaging.version import parse as parse_version, InvalidVersion

###############################################################################
## We bundle the logic for inferring metadata from a repository here, so that
## the rules can be easily tested and updated.
##
## This may contain lightweight business logic such as email validation,
## semantic version parsing, and rules defined by the CDC Enterprise
## Architect (EA) team.
###############################################################################
class Inference:

  # --- Define Non-Code Languages ---
  NON_CODE_LANGUAGES = [
    'markdown', 'text', 'html', 'css', 'xml', 'yaml', 'json', 'shell',
    'batchfile', 'powershell', 'dockerfile', 'makefile', 'cmake',
    'tex', 'roff', 'csv', 'tsv'
  ]

  # --- Define Exemption Codes as Constants ---
  EXEMPT_BY_LAW = "exemptByLaw"
  EXEMPT_BY_NATIONAL_SECURITY = "exemptByNationalSecurity"
  EXEMPT_BY_AGENCY_SYSTEM = "exemptByAgencySystem"
  EXEMPT_BY_MISSION_SYSTEM = "exemptByMissionSystem"
  EXEMPT_BY_CIO = "exemptByCIO"

  VALID_EXEMPTION_CODES = [
    EXEMPT_BY_LAW,
    EXEMPT_BY_NATIONAL_SECURITY,
    EXEMPT_BY_AGENCY_SYSTEM,
    EXEMPT_BY_MISSION_SYSTEM,
    EXEMPT_BY_CIO
  ]

  def __init__(self):
    """Initializes the Sanitizer with configuration and regex patterns."""
    self.email_regex = re.compile(r'[\w.+-]+@cdc\.gov')

    # Case-insensitive regex to find "Key: Value" at the start of a line
    self.marker_regex_template = r'(?i)^\s*{}:\s*(.*)$'

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

  def infer_organization(self, repo_name, readme_content):
    """Infers the organization based on README markers and repository name."""
    # 1. README Marker (highest priority)
    try:
      org_from_readme = self._parse_marker(readme_content, 'Organization|Org')
      if org_from_readme:
        return org_from_readme
    except Exception as e:
      print(f"Error parsing organization from README for {repo_name}: {e}")

    # 2. Programmatic Check for known acronyms in repo name
    repo_name_lower = repo_name.lower()
    organization = Organization()
    for acronym, full_name in organization.get().items():
      acronym_lower = acronym.lower()
      if f"{acronym_lower}-" in repo_name_lower or f"-{acronym_lower}" in repo_name_lower:
        return full_name

    # 3. Default to agency name
    config = Config()
    return config.DEFAULT_AGENCY_NAME

  def infer_contact_email(self, is_private, readme_content, codeowners_content):
    config = Config()

    """Infers the contact email based on visibility, README, and CODEOWNERS."""
    if is_private:
      return config.PRIVATE_REPO_CONTACT_EMAIL

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
    return config.DEFAULT_CONTACT_EMAIL

  def infer_status(self, is_archived, pushed_at, readme_content):
    """Infers the repository status with a defined order of precedence."""
    # 1. Archived status from platform
    if is_archived:
      return "archived"

    # 2. Status marker in README
    status_from_readme = self._parse_marker(readme_content, 'Status')
    if status_from_readme:
      return status_from_readme.lower()

    # 3. Inactive check (no modifications for over 2 years)
    now = datetime.now(timezone.utc)
    last_modified = pushed_at.replace(tzinfo=timezone.utc)
    if (now - last_modified).days > 730:
      return "inactive"

    # 4. Default status
    return "development"

  def infer_version(self, tags, readme_content):
    """Infers the version from tags or a README marker."""
    # 1. Scan tags for the latest valid semantic version
    latest_version = None
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

  def infer_usage_and_url(self, is_private, license, html_url, readme_content, languages):
    """Determines usageType, exemptionText, and repositoryURL based on a set of rules."""
    config = Config()

    # --- Public Repositories ---
    if not is_private:
      usage_type = "openSource" if license else "governmentWideReuse"
      return usage_type, None, html_url

    # --- Private or Internal Repositories ---
    # 1. Manual README Marker (highest priority)
    exemption_type_from_marker = self._parse_marker(readme_content, 'Exemption')
    if exemption_type_from_marker and exemption_type_from_marker in self.VALID_EXEMPTION_CODES:
      justification = self._parse_marker(readme_content, 'Exemption justification')
      url = config.EXEMPTED_NOTICE_PDF_URL
      return exemption_type_from_marker, justification, url

    # 2. Non-Code Check
    # A repository with no detected languages is also considered non-code.
    if not languages or all(lang.lower() in self.NON_CODE_LANGUAGES for lang in languages if lang):
      usage_type = self.EXEMPT_BY_CIO
      justification = "Repository contains no code or only non-code assets like documentation and configuration."
      url = config.EXEMPTED_NOTICE_PDF_URL
      return usage_type, justification, url

    # 3. Default for private/internal repos
    usage_type = "governmentWideReuse"
    url = config.INSTRUCTIONS_PDF_URL
    return usage_type, None, url
