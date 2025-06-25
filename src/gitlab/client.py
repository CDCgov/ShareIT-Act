import base64
import dateutil.parser
import gitlab
import requests

from typing import Dict, List, Any

class GitlabClient:
  def __init__(self, url: str = "https://gitlab.com", token: str = None, socks_proxy: str = None, verify_ssl: bool = True):
    self.url = url
    self.token = token
    self.socks_proxy = socks_proxy

    session = None
    if socks_proxy:
      session = requests.Session()
      session.proxies = {
        'http': socks_proxy,
        'https': socks_proxy
      }
      session.verify = verify_ssl
    self.gl = gitlab.Gitlab(self.url, private_token=self.token, session=session, ssl_verify=verify_ssl)

  def get_all_repos(self) -> List[Dict[str, Any]]:
    try:
      all_groups = self.gl.groups.list(all=True)
      all_repos = []

      for group in all_groups:
        print(f"Fetching repositories from group: {group.name} (ID: {group.id})")
        try:
          projects = group.projects.list(all=True, include_subgroups=True)
          for project in projects:
            metadata = self.get_repository_metadata(project.id)
            if metadata:
              all_repos.append(metadata)
        except Exception as e:
          print(f"Error fetching projects from group {group.name}: {e}")

      return all_repos
    except Exception as e:
      print(f"Error fetching all GitLab repositories: {e}")
      return []

  def get_repos(self, config: Dict[str, Any]) -> List[Dict[str, Any]]:
    group_id = config.get("gitlab_group_id")
    if not group_id:
      return []

    try:
      group = self.gl.groups.get(group_id)
      projects = group.projects.list(all=True, include_subgroups=True)
      return [self.get_repository_metadata(project.id) for project in projects]
    except Exception as e:
      print(f"Error fetching GitLab repositories: {e}")
      return []

  def get_repository_metadata(self, project_id: int) -> Dict[str, Any]:
    try:
      project = self.gl.projects.get(project_id, lazy=False)
      languages = project.languages() or {}

      created_at_dt = None
      if project.created_at:
        created_at_dt = dateutil.parser.parse(project.created_at)

      last_activity_at_dt = None
      if project.last_activity_at:
        last_activity_at_dt = dateutil.parser.parse(project.last_activity_at)

      readme_content = ""
      readme_html_url = None
      try:
        readme = project.repository_tree(path="", ref=project.default_branch, all=True, recursive=False, search="README")
        if readme and len(readme) > 0:
          readme_file = readme[0]
          readme_path = readme_file.get("path")
          readme_html_url = f"{project.web_url}/-/blob/{project.default_branch}/{readme_path}"
          raw_file = project.files.get(file_path=readme_path, ref=project.default_branch)
          readme_content = base64.b64decode(raw_file.content).decode('utf-8', errors='replace')
      except:
        pass

      codeowners_content = ""
      try:
        codeowners_paths = ["CODEOWNERS", ".github/CODEOWNERS", ".gitlab/CODEOWNERS", "docs/CODEOWNERS"]
        for path in codeowners_paths:
          try:
            codeowners_file = project.files.get(file_path=path, ref=project.default_branch)
            codeowners_content = base64.b64decode(codeowners_file.content).decode('utf-8', errors='replace')
            break
          except:
            continue
      except:
        pass

      repo_tags = []
      try:
        tags = project.tags.list(all=True)
        repo_tags = [tag.name for tag in tags]
      except:
        pass

      licenses_list = []
      if project.license:
        license_name = project.license.get("name", "")
        if license_name:
          licenses_list.append({
            "name": license_name,
            "URL": f"{project.web_url}/-/blob/{project.default_branch}/LICENSE"
          })

      visibility_status = "private"
      if project.visibility == "public":
        visibility_status = "public"

      topic_tags = project.topics if hasattr(project, "topics") else []

      return {
        "description": project.description,
        "repositoryURL": project.web_url,
        "homepageURL": project.web_url,
        "downloadURL": None,
        "readme_url": readme_html_url,
        "vcs": "git",
        "repositoryVisibility": visibility_status,
        "status": "development",
        "version": "N/A",
        "laborHours": 0,
        "languages": list(languages.keys()),
        "tags": topic_tags,
        "date": {
          "created": created_at_dt.isoformat() if created_at_dt else None,
          "lastModified": last_activity_at_dt.isoformat() if last_activity_at_dt else None,
        },
        "permissions": {
          "usageType": None,
          "exemptionText": None,
          "licenses": licenses_list
        },
        "contact": {},
        "contractNumber": None,
        "readme_content": readme_content,
        "_codeowners_content": codeowners_content,
        "_api_tags": repo_tags,
        "archived": project.archived
      }
    except Exception as e:
      print(f"Error fetching repository metadata for project ID {project_id}: {e}")
      return {}

def main():
  import argparse

  parser = argparse.ArgumentParser(description='Fetch GitLab repository metadata')
  parser.add_argument('--url', default='https://gitlab.com', help='GitLab instance URL')
  parser.add_argument('--token', required=True, help='GitLab personal access token')
  parser.add_argument('--group-id', help='GitLab group ID (optional if --all is used)')
  parser.add_argument('--all', action='store_true', help='Fetch repositories from all accessible groups')
  parser.add_argument('--socks-proxy', help='SOCKS proxy URL (e.g., socks5h://127.0.0.1:1080)')
  parser.add_argument('--no-verify-ssl', action='store_true', help='Disable SSL verification')
  parser.add_argument('--output', default='gitlab-repos.json', help='Output JSON file')
  args = parser.parse_args()

  import json
  from pathlib import Path
  gitlab_client = GitlabClient(url=args.url, token=args.token, socks_proxy=args.socks_proxy, verify_ssl=not args.no_verify_ssl)

  if args.all:
    print("Fetching repositories from all accessible groups...")
    repos = gitlab_client.get_all_repos()
  elif args.group_id:
    print(f"Fetching repositories from GitLab group {args.group_id}...")
    config = {"gitlab_group_id": args.group_id}
    repos = gitlab_client.get_repos(config)
  else:
    print("Error: Either --group-id or --all must be specified")
    return

  print(f"Found {len(repos)} repositories")

  output_path = Path(args.output)
  with open(output_path, 'w') as f:
    json.dump(repos, f, indent=2)

  print(f"Repository metadata saved to {output_path}")

if __name__ == "__main__":
  main()

