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
      'github_app_private_key': os.environ.get('GH_APP_PRIVATE_KEY', '')
    }

  def verify(self):
    errors = ''
    if os.environ.get('GH_ORG', '') == '':
      errors += 'github org'
    if os.environ.get('GH_APP_INSTALLATION_ID', '') == '':
      if errors != '':
        errors += ', '
      errors += 'github app installation id'
    else:
      try:
        int(os.environ.get('GH_APP_INSTALLATION_ID', '0'))
      except ValueError:
        if errors != '':
          errors += ', '
        errors += 'github app installation id is not a valid integer'
    if os.environ.get('GH_APP_ID', '') == '':
      if errors != '':
        errors += ', '
      errors += 'github app id'
    else:
      try:
        int(os.environ.get('GH_APP_ID', '0'))
      except ValueError:
        if errors != '':
          errors += ', '
        errors += 'github app id is not a valid integer'
    if os.environ.get('GH_APP_PRIVATE_KEY', '') == '':
      if errors != '':
        errors += ', '
      errors += 'github app private key'
    if errors != '':
      errors += " is not set."
      return errors, False
    return errors, True
