from src.config import Config
from src.repository import Repository
from src.sanitize import Sanitizer
from src.combine import Combine

from datetime import datetime
from pathlib import Path
import sys
import json
import argparse

###############################################################
## The intention is to provide a simple interface to update
## us with existing repositories in a Github organization, and
## then sanitize the data to a common format such as code.json
## to provide the user with all of the known repositories.
###############################################################
def main():
  parser = argparse.ArgumentParser(description='Process GitHub organization')
  parser.add_argument('--output', help='Output directory path')
  parser.add_argument('--combine', action='store_true', help='Combine all JSON files in data/raw directory')
  args = parser.parse_args()

  now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
  print(f"Process starting: {now}")

  if args.combine:
    credentials = Config().credentials()
    input_dir = credentials.get('raw_data_dir', 'data/raw')
    if input_dir == 'data/raw':
      input_dir = str(Path(__file__).parent.absolute() / 'data/raw')
    Combine().combine_json_files(input_dir, args.output)
    now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    print(f"Completed processing at {now}")
    return

  errors, isVerified = Config().verify()
  if errors or not isVerified:
    print(f'Exiting due to bad credentials in configuration: {errors}')
    sys.exit(1)

  credentials = Config().credentials()
  print(f'Targeting GitHub organization: https://github.com/{credentials.get("github_org", "")}')
  if args.output:
    credentials['raw_data_dir'] = args.output
  elif credentials.get('raw_data_dir') == 'data/raw':
    credentials['raw_data_dir'] = str(Path(__file__).parent.absolute() / 'data/raw')
  print(f'Raw data directory: {credentials["raw_data_dir"]}')
  org_name = credentials.get('github_org', '')
  repos = Repository().get_repos(credentials)

  sanitizer = Sanitizer()
  sanitized_data = []
  for repo in repos:
    data = sanitizer.get_repository_metadata(repo)
    sanitized_data.append(data)
  output_dir = Path(credentials["raw_data_dir"])
  output_dir.mkdir(parents=True, exist_ok=True)
  output_file = output_dir / f"repo-{org_name}.json"
  with open(output_file, 'w') as f:
    json.dump(sanitized_data, f, indent=2)
  print(f"Data saved to {output_file}")

  now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
  print(f"Completed processing at {now}")

if __name__ == "__main__":
  main()
