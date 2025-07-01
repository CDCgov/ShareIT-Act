import argparse
import os
import json
import pytz

from pathlib import Path
from client import GitlabClient
from datetime import datetime
from dotenv import load_dotenv
load_dotenv()

def main():
  parser = argparse.ArgumentParser(description='Fetch GitLab repository metadata')
  parser.add_argument('--url', default='https://gitlab.com', help='GitLab instance URL')
  parser.add_argument('--group-id', help='GitLab group ID (optional, fetches all accessible groups if not provided)')
  parser.add_argument('--socks-proxy', help='SOCKS proxy URL (e.g., socks5h://127.0.0.1:1080)')
  parser.add_argument('--no-verify-ssl', action='store_true', help='Disable SSL verification')
  parser.add_argument('--output', help='Output JSON file')
  args = parser.parse_args()

  tz = pytz.timezone('UTC')
  start_time = datetime.now(tz)
  print(f"Process starting at: {start_time.isoformat()}")

  access_token = os.environ.get('GITLAB_TOKEN', '')
  if not access_token:
    print("Error: GitLab token is required. Please provide it by setting the GITLAB_TOKEN environment variable.")
    return
  gitlab_client = GitlabClient(url=args.url,
    token=access_token,
    socks_proxy=args.socks_proxy,
    verify_ssl=not args.no_verify_ssl
  )

  if args.group_id:
    print(f"Fetching repositories from GitLab group {args.group_id}...")
    config = {"gitlab_group_id": args.group_id}
    repos = gitlab_client.get_repos(config)
    print(f"Found {len(repos)} total repositories")
  else:
    print("Fetching repositories from all accessible groups...")
    repos = gitlab_client.get_all_repos()
    print(f"Found {len(repos)} total repositories")

  if args.output:
    output_path = Path(args.output)
  else:
    url = os.environ.get('GITLAB_URL', args.url)
    safe_url = url.replace("https://", "").replace("http://", "").replace("/", "-")
    output_path = Path("data/raw") / f"repo-{safe_url}.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)

  with open(output_path, 'w') as f:
    json.dump(repos, f, indent=2)

  end_time = datetime.now(tz)
  duration = end_time - start_time
  print(f"Repository metadata saved to {output_path}")
  print(f"Process completed at: {end_time.isoformat()}")
  print(f"Total execution time: {duration}")

if __name__ == "__main__":
  main()
