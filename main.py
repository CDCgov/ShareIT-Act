from src.codejson import CodeJson
from src.config import Config
from src.repository import Repository
from src.sanitize import Sanitizer

from datetime import datetime
from pathlib import Path
import sys

def main():
  now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
  print(now)
  errors, isVerified = Config().verify()
  if errors or not isVerified:
    print(f'Exiting due to bad credentials in configuration: {errors}')
    sys.exit()
  credentials = Config().credentials()
  if credentials.get('raw_data_dir') == 'data/raw':
    credentials['raw_data_dir'] = str(Path(__file__).parent.absolute() / 'data/raw')
  print(f'Raw data directory: {credentials["raw_data_dir"]}')

  from pprint import pprint
  repos = Repository().get_repos(credentials)
  pprint(repos)
  sanitizer = Sanitizer()
  for repo in repos:
    data = sanitizer.get_repository_metadata(repo)
    pprint(data)




if __name__ == "__main__":
  main()
