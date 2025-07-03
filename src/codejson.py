
"""
This module includes a set of rules defined by the CDC Enterprise Architecture (EA) team on
how to populate the code.json metadata for a given repository.

The rules are listed as comments in each function to provide context on how the values
are derived or inferred.
"""
class CodeJson:

  def get_header(self):
    header = {
      "version": "2.0",
      "agency": "CDC",
      "measurementType": {
        "method": "projects"
      }
    }
    return header

  def get_required_project_fields(self):
    required_fields = {
      "name": "",
      "description": "",
      "organization": "",
      "repositoryURL": "",
      "repositoryVisibility": "",
      "permissions": {
        "usageType": "",
        "exemptionText": "",
        "licenses": [
          {
            "name": ""
          }
        ]
      }
    }
    return required_fields

  def get_all_project_fields(self):
    all_fields = {
      "name": "",
      "description": "",
      "organization": "",
      "repositoryURL": "",
      "homepageURL": "",
      "vcs": "",
      "repositoryVisibility": "",
      "status": "",
      "version": "",
      "laborHours": 0,
      "languages": [],
      "tags": [],
      "date": {
        "created": "",
        "lastModified": "",
        "metadataLastUpdated": "",
      },
      "permissions": {
        "usageType": "",
        "exemptionText": "",
        "licenses": [
          {
            "name": ""
          }
        ]
      },
      "contact": {
        "email": "",
        "name": ""
      },
      "repo_id": 0,
      "readme_url": "",
      "privateID": ""
    }
    return all_fields

  def get_usage_type(self, is_public, licenseType, has_license=False):
    """
    For public repositories:
    If a license file is provided, the usageType is set to openSource.
    If no license is found, it defaults to governmentWideReuse.

    For private or internal repositories:
    We follow these steps in order on determining usageType:
    1. We look for the words "exemption" and "exemption justification" markers in the README.md file.
       If they exist, usageType is set to the exemption, and the text for the justification ends up with exemptionText.
    2. We checks the repository's programming languages. If the repo contains only non-code content (like Markdown, text, HTML/CSS, shell scripts, etc.), usageType is set to exemptNonCode.
    3. AI Exploratory Check: If we can use AI to infer on the repository, we'll prompt the AI to verify whether the repository's primary purpose is experimental, a demo, a tutorial, or a proof-of-concept. If so, it's exempted (usually as exemptByCIO) with a justification explaining why.
    4. AI General Exemption Check: If we can use AI to infer on the repository, we'lll prompt the AI to verify for other specific exemptions based on the repository's name, description, and README content.
    5. Default: If none of the above conditions are met, the usageType defaults to governmentWideReuse.
    """
    return "governmentWideReuse"

  def get_exemption_text(self):
    """
    This is a reason for exemption and only populated if the usageType is an exemption.
    """
    pass

  def get_repository_url(self, is_public, is_exempt=False):
    """
    For public repositories: The URL is the direct and publicly accessible link to the repository.
    For private or internal repositories: The URL is intentionally replaced.
    If the repository is exempt, the URL points to https://github.com/CDCgov/ShareIT-Act/blob/main/docs/assets/files/code_exempted.pdf
    If the repository is not exempt (eg. governmentWideReuse), the URL points to a standard instructions page: https://github.com/CDCgov/ShareIT-Act/blob/main/docs/assets/files/instructions.pdf
    """
    pass

  def get_organization(self):
    """
    The tool uses a multi-step process to infer the correct organizational owner:
    Programmatic Check: It first checks the repository name for known acronyms (e.g., a repo named ocio-project would be mapped to the "Office of the Chief Information Officer").
    README Marker: It then looks for an Organization: or Org: : marker in the README.md file. If found, this value will override any previous inference.
    AI Inference (Fallback): If the organization is still a generic one (e.g., just "CDC") and AI is enabled, the AI analyzes the repository's content to suggest a more specific organization from a known list.
    Agency Default: If, after all checks, the organization is still a generic top-level name, it defaults to the AGENCY_NAME configured for the tool (e.g., "CDC").
    """
    pass

  def get_private_id(self, git_instance, id):
    """
    A unique identifier for the repository within its hosting platform.
    For GitHub, this is the github_<repository_id> (an integer).
    For GitLab, it's the gitlab_<project_id> (also an integer).
    """
    return f"{git_instance}_{id}"

  def get_description(self):
    """
    The tool starts with the description provided by the platform (e.g., the description you see on the GitHub repository page).
    If that description is missing or empty and AI is enabled, the tool will ask the AI to generate a concise, 1-2 sentence summary based on the README.md content.
    """
    pass

  def get_contact_email(self):
    """
    For Public Repositories: It searches for a @cdc.gov email address in the following order of priority:
    1. Find the email in the README.md file.
    2. Find the email in the CODEOWNERS file.
    3. If no email is found, it defaults to shareit@cdc.gov.
    For Private or Internal Repositories: It always uses the PRIVATE_REPO_CONTACT_EMAIL from the configuration for consistency and privacy.
    """
    return "shareit@cdc.gov"

  def get_status(self):
    """
    The repository status is inferred with the following precedence:
    archived: If the repository is marked as "archived" on the platform.
    inactive: If the repository has not been modified in over 2 years.
    development: The default status if none of the above apply.
    """
    return "development"

  def get_version(self):
    return "N/A"
