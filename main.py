import argparse
import csv
import sys
import json

from src.config import Config
from src.repository import Repository
from src.sanitize import Sanitizer
from src.combine import Combine

from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from pathlib import Path

def generate_privateid_csv(code_json_path, csv_path):
  code_json_path = Path(code_json_path)
  csv_path = Path(csv_path)
  if not code_json_path.exists():
    print(f"code.json not found at {code_json_path}")
    return

  with open(code_json_path, "r") as f:
    code_data = json.load(f)

  existing_ids = set()
  rows = []
  if csv_path.exists():
    with open(csv_path, "r", newline='') as f:
      reader = csv.DictReader(f, delimiter=',')
      for row in reader:
        existing_ids.add(row["PrivateID"])
        rows.append(row)

  new_rows = []
  for repo in code_data.get('projects', []):
    if not isinstance(repo, dict):
      continue
    repo_id = repo.get("repo_id")
    if not repo_id:
      continue
    private_id = f"github_{repo_id}"
    if private_id in existing_ids:
      continue
    if repo.get("platform", "") == "AzureDevOps":
      private_id = f"azuredevops_{repo_id}"
    repo_url = repo.get("repositoryURL", "")
    repo_name = repo_url.rstrip("/").split("/")[-1]
    org = repo.get("organization", "") or (repo_url.rstrip("/").split("/")[-2] if "/" in repo_url else "")
    contact_emails = ""
    contact = repo.get("contact", {})
    if isinstance(contact, dict):
      emails = []
      for v in contact.values():
        if isinstance(v, str) and "@" in v:
          emails.append(v)
        elif isinstance(v, list):
          emails.extend([e for e in v if "@" in e])
      contact_emails = ",".join(emails)
    date_added = datetime.now().isoformat()
    new_rows.append({
      "PrivateID": private_id,
      "RepositoryName": repo_name,
      "RepositoryURL": repo_url,
      "Organization": org,
      "ContactEmails": contact_emails,
      "DateAdded": date_added
    })

  fieldnames = ["PrivateID", "RepositoryName", "RepositoryURL", "Organization", "ContactEmails", "DateAdded"]
  with open(csv_path, "w", newline='') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=',')
    writer.writeheader()
    for row in rows:
      writer.writerow(row)
    for row in new_rows:
      writer.writerow(row)
  print(f"CSV mapping written to {csv_path}")

def sanitize_repo(sanitizer, repo):
  return sanitizer.get_repository_metadata(repo)

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
  parser.add_argument('--filter', action='store_true', help='Filter repositories by criteria, only used with --combine')
  parser.add_argument('--public-only', action='store_true', help='Filter repositories by public repositories, only used with --combine')
  parser.add_argument('--generate-csv', action='store_true', help='Generate privateid_mapping.csv from code.json')
  parser.add_argument('--repo-id', help='Run inference for a single repo ID and output one file')
  args = parser.parse_args()

  now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
  print(f"Process starting: {now}")

  if args.combine and args.filter:
    credentials = Config().credentials()
    input_dir = credentials.get('raw_data_dir', 'data/raw')
    if input_dir == 'data/raw':
      input_dir = str(Path(__file__).parent.absolute() / 'data/raw')
    Combine().combine_json_files_with_filter(input_dir, args.output)
    now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    print(f"Completed processing at {now}")
    return

  elif args.combine and args.public_only:
    credentials = Config().credentials()
    input_dir = credentials.get('raw_data_dir', 'data/raw')
    if input_dir == 'data/raw':
      input_dir = str(Path(__file__).parent.absolute() / 'data/raw')
    Combine().combine_json_files_with_public(input_dir, args.output)
    now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    print(f"Completed processing at {now}")
    return

  elif args.combine and not args.filter and not args.public_only:
    credentials = Config().credentials()
    input_dir = credentials.get('raw_data_dir', 'data/raw')
    if input_dir == 'data/raw':
      input_dir = str(Path(__file__).parent.absolute() / 'data/raw')
    Combine().combine_json_files(input_dir, args.output)
    now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    print(f"Completed processing at {now}")
    return

  if args.generate_csv:
    output_dir = Path(args.output) if args.output else Path(__file__).parent / "data"
    code_json_path = output_dir / "code.json"
    csv_path = output_dir / "privateid_mapping.csv"
    print(code_json_path, csv_path)
    generate_privateid_csv(code_json_path, csv_path)
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
  sanitizer = Sanitizer()

  if args.repo_id:
    repo_id = args.repo_id
    repo = Repository(credentials).get_repo_by_id(repo_id)
    if not repo:
      print(f"Repository with id {repo_id} not found.")
      sys.exit(1)
    data = sanitizer.get_repository_metadata(repo)
    output_dir = Path(credentials["raw_data_dir"])
    output_dir.mkdir(parents=True, exist_ok=True)
    output_file = output_dir / f"repo-{repo_id}.json"
    with open(output_file, 'w') as f:
      json.dump(data, f, indent=2)
    print(f"Single repository metadata saved to {output_file}")
    now = datetime.now().strftime("%Y-%m-%dT%H-%M-%S")
    print(f"Completed processing at {now}")
    return

  repos = Repository(credentials).get_repos()
  sanitized_data = []
  MAX_THREADS = 4

  with ThreadPoolExecutor(max_workers=MAX_THREADS) as executor:
    futures = [executor.submit(sanitize_repo, sanitizer, repo) for repo in repos]
    for future in as_completed(futures):
      data = future.result()
      if data:
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
