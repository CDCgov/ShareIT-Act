import os
from dotenv import load_dotenv

load_dotenv()

class Config:
  def credentials(self):
    return {
      'github_org': os.environ.get('GITHUB_ORG', ''),
      'github_app_id': os.environ.get('GITHUB_APP_ID', ''),
      'github_app_installation_id': os.environ.get('GITHUB_APP_INSTALLATION_ID', ''),
      'github_app_private_key': os.environ.get('GITHUB_APP_PRIVATE_KEY', '')
    }

  def verify(self):
    errors = ''
    if os.environ.get('GITHUB_ORG', '') == '':
      errors += 'github org'
    if os.environ.get('GITHUB_APP_ID', '') == '':
      if errors != '':
        errors += ', '
      errors += 'github app id'
    if os.environ.get('GITHUB_APP_INSTALLATION_ID', '') == '':
      if errors != '':
        errors += ', '
      errors += 'github app installation id'
    if os.environ.get('GITHUB_APP_PRIVATE_KEY', '') == '':
      if errors != '':
        errors += ', '
      errors += 'github app private key'
    if errors != '':
      errors += " is not set."
      return errors, False
    return errors, True
