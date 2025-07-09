import os
from dotenv import load_dotenv

load_dotenv()

class Config:
  def get_app_config(self):
    """Returns application-specific configurations."""
    return {
      'AGENCY_NAME': os.environ.get('AGENCY_NAME', 'CDC'),
      'DEFAULT_CONTACT_EMAIL': os.environ.get('DEFAULT_CONTACT_EMAIL', 'cdcinfo@cdc.gov'),
      'PRIVATE_REPO_CONTACT_EMAIL': os.environ.get('PRIVATE_REPO_CONTACT_EMAIL', 'shareit@cdc.gov'),
      'EXEMPTED_NOTICE_PDF_URL': os.environ.get(
        'EXEMPTED_NOTICE_PDF_URL',
        'https://cdcgov.github.io/ShareIT-Act/assets/files/code_exempted.pdf'
      ),
      'INSTRUCTIONS_PDF_URL': os.environ.get(
        'INSTRUCTIONS_PDF_URL',
        'https://cdcgov.github.io/ShareIT-Act/assets/files/instructions.pdf'
      ),
      'NON_CODE_LANGUAGES': [
          'markdown', 'text', 'html', 'css', 'shell', 'dockerfile', 'powershell'
      ],
      'ORG_ACRONYMS': {
        "cdc": "Centers for Disease Control and Prevention", "od": "Office of the Director",
        "om": "Office of Mission Support", "ocoo": "Office of the Chief Operating Officer",
        "oadc": "Office of the Associate Directory of Communications",
        "ocio": "Office of the Chief Information Officer",
        "oed": "Office of Equal Employment Opportunity and Workplace Equity",
        "oga": "Office of Global Affairs", "ohs": "Office of Health Equity",
        "opa": "Office of Policy, Performance, and Evaluation",
        "ostlts": "Office of State, Tribal, Local and Territorial Support",
        "owcd": "Office of Women’s Health and Health Equity",
        "cSELS": "Center for Surveillance, Epidemiology, and Laboratory Services",
        "csels": "Center for Surveillance, Epidemiology, and Laboratory Services",
        "ddphss": "Deputy Director for Public Health Science and Surveillance",
        "cgH": "Center for Global Health", "cgh": "Center for Global Health",
        "cid": "Center for Preparedness and Response", "cpr": "Center for Preparedness and Response",
        "ncezid": "National Center for Emerging and Zoonotic Infectious Diseases",
        "ncird": "National Center for Immunization and Respiratory Diseases",
        "nchhstp": "National Center for HIV, Viral Hepatitis, STD, and TB Prevention",
        "nccdphp": "National Center for Chronic Disease Prevention and Health Promotion",
        "nceh": "National Center for Environmental Health",
        "atsdr": "Agency for Toxic Substances and Disease Registry",
        "ncipc": "National Center for Injury Prevention and Control",
        "ncbddd": "National Center on Birth Defects and Developmental Disabilities",
        "nchs": "National Center for Health Statistics",
        "niosh": "National Institute for Occupational Safety and Health",
        "ddid": "Deputy Director for Infectious Diseases",
        "ddnidd": "Deputy Director for Non-Infectious Diseases",
        "cfa": "Center for Forecasting and Outbreak Analytics",
        "ophdst": "Office of Public Health Data, Surveillance, and Technology",
        "amd": "Office of Advanced Molecular Detection", "oamd": "Office of Advanced Molecular Detection",          
      }
    }
  def _get_credentials_from_env(self, org_name=None):
#  def credentials(self, org_name=None):
    # Use uppercase org_name as a prefix for environment variables
    prefix = f"{org_name.upper()}_" if org_name else ""

    app_id = os.environ.get(f'{prefix}GH_APP_ID', '0')
    installation_id = os.environ.get(f'{prefix}GH_APP_INSTALLATION_ID', '0')
    try:
      app_id = int(app_id) if app_id else 0
    except ValueError:
      app_id = 0
    try:
      installation_id = int(installation_id) if installation_id else 0
    except ValueError:
      installation_id = 0

    # Read the private key directly from the file mounted into the container.
    # This is the most robust method for handling multi-line secrets.
    private_key = ""
    key_path = f"/app/secure/{org_name.lower()}_key.pem"
    try:
        # Read the key as a string and normalize newlines to satisfy the PyGithub library.
        with open(key_path, 'r') as f:
            # Read the file, strip leading/trailing whitespace, and split into lines
            lines = f.read().strip().splitlines()
            # Strip each line and join back with the correct newline character
            private_key = "\n".join(line.strip() for line in lines)
    except FileNotFoundError:
        print(f"Warning: Private key file not found at {key_path}. Authentication will likely fail.")

    return {
      'raw_data_dir' : os.environ.get('RAW_DATA_DIR', 'data/raw'),
      'github_org': org_name or os.environ.get('GH_ORG', ''),
      'github_app_id': app_id,
      'github_app_installation_id': installation_id,
      'github_app_private_key': private_key,
      'github_token': os.environ.get(f'{prefix}GH_PAT_TOKEN', '')
    }
  def _validate_credentials(self, creds):
    """Validates the provided credentials dictionary and returns a list of errors."""
    errors = []
    
#  def verify_github_credentials(self, creds):
#    errors = []
    if not creds.get('github_org'):
        errors.append("GitHub organization is not specified")

    # If a PAT is provided and valid, we don't need to check for App credentials
    if creds.get('github_token'):
      if not creds['github_token'].startswith(('ghp_', 'github_pat_')):
        errors.append("GitHub token appears to be invalid (should start with 'ghp_' or 'github_pat_')")
      else:
        # Token auth is valid, no need to check App creds further.
        # If org is also missing, that error will be returned.
        return errors
      
    has_app_id = creds.get('github_app_id')
    has_installation_id = creds.get('github_app_installation_id')
    has_private_key = creds.get('github_app_private_key')
    if not (has_app_id and has_installation_id and has_private_key):
        missing = []
        prefix = creds.get("prefix", "")
        if not has_app_id:
            missing.append(f'{prefix}GH_APP_ID')
        if not has_installation_id:
            missing.append(f'{prefix}GH_APP_INSTALLATION_ID')
        if not has_private_key:
            missing.append(f'{prefix}GH_APP_PRIVATE_KEY_PATH')
        
        if missing:
              errors.append(f"Missing GitHub App credentials. Either provide a valid GH_PAT_TOKEN or all of the following: {', '.join(missing)}")

    return errors

  def get_and_verify_credentials(self, org_name=None):
    """
    Gets and validates credentials for a given organization.
    Returns a tuple of (credentials, errors).
    """
    creds = self._get_credentials_from_env(org_name)
    errors = self._validate_credentials(creds)
    return creds, errors
