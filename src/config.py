import os
from dotenv import load_dotenv

load_dotenv()

class Config:
  def credentials(self):
    app_id = os.environ.get('GH_APP_ID', '0')
    installation_id = os.environ.get('GH_APP_INSTALLATION_ID', '0')
    try:
      app_id = int(app_id) if app_id else 0
    except ValueError:
      app_id = 0

    try:
      installation_id = int(installation_id) if installation_id else 0
    except ValueError:
      installation_id = 0
    return {
      'raw_data_dir' : os.environ.get('RAW_DATA_DIR', 'data/raw'),
      'github_org': os.environ.get('GH_ORG', ''),
      'github_app_id': app_id,
      'github_app_installation_id': installation_id,
      'github_app_private_key': os.environ.get('GH_APP_PRIVATE_KEY', ''),
      'github_pat': os.environ.get('GH_PAT_TOKEN', '')
    }

  def verify_github_credentials(self, config):
    errors = []
    using_app = False
    using_pat = False
    if any(key in config for key in ['github_app_id', 'github_app_installation_id', 'github_app_private_key']):
      using_app = True
      if 'github_app_id' not in config or not config['github_app_id']:
        errors.append("GitHub App ID is missing")
      if 'github_app_installation_id' not in config or not config['github_app_installation_id']:
        errors.append("GitHub App Installation ID is missing")
      if 'github_app_private_key' not in config or not config['github_app_private_key']:
        errors.append("GitHub App Private Key is missing")
      elif not config['github_app_private_key'].strip().startswith('-----BEGIN RSA PRIVATE KEY-----'):
        errors.append("GitHub App Private Key is invalid (must be a valid RSA private key)")
    if 'github_token' in config and config['github_token']:
      using_pat = True
      if not config['github_token'].startswith(('ghp_', 'github_pat_')):
        errors.append("GitHub token appears to be invalid (should start with 'ghp_' or 'github_pat_')")
    if using_app and using_pat:
      errors.append("Both GitHub App and Personal Access Token configured. Please use only one authentication method.")
    if not using_app and not using_pat:
      errors.append("No GitHub authentication configured. Please provide either GitHub App credentials or a Personal Access Token.")
    is_valid = len(errors) == 0
    return errors, is_valid

  def verify(self):
    config = self.credentials()
    errors, is_valid = self.verify_github_credentials(config)
    if 'github_org' not in config or not config['github_org']:
      errors.append("GitHub organization is not specified")
      is_valid = False
    return errors, is_valid
