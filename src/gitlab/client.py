
from typing import Dict, List, Any

import base64
import dateutil.parser
import gitlab
import requests

class GitlabClient:
  def __init__(self, url: str = "https://gitlab.com",
               token: str = None,
               socks_proxy: str = None,
               verify_ssl: bool = True):
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
    if self.socks_proxy:
      print(f"Initialized GitLab client with SOCKS proxy: {self.socks_proxy}")
      ## Suppress InsecureRequestWarning if SSL verification is disabled
      ## as socks proxy generally does not support SSL verification
      import urllib3
      urllib3.disable_warnings()

  def get_all_repos(self) -> List[Dict[str, Any]]:
    try:
      print("Fetching all accessible projects (repositories)...")
      all_projects = self.gl.projects.list(all=True)
      print(f"Total accessible repositories: {len(all_projects)}")
      all_repos = []
      repo_count = 0
      for project in all_projects:
        print(f"Processing repository: {project.name} (ID: {project.id})")
        metadata = self.get_repository_metadata(project.id)
        if metadata:
          all_repos.append(metadata)
          repo_count += 1
        print(f"Processed repositories: {repo_count} from project ID {project.id} - {project.name}")
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
      print(f"Fetching repositories from group: {group.name} (ID: {group.id})")
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

      # readme_content = ""
      readme_html_url = None
      try:
        readme = project.repository_tree(path="", ref=project.default_branch, all=True, recursive=False, search="README")
        if readme and len(readme) > 0:
          readme_file = readme[0]
          readme_path = readme_file.get("path")
          readme_html_url = f"{project.web_url}/-/blob/{project.default_branch}/{readme_path}"
          # raw_file = project.files.get(file_path=readme_path, ref=project.default_branch)
          # readme_content = base64.b64decode(raw_file.content).decode('utf-8', errors='replace')
      except Exception as e:
        print(f"Error fetching README for project ID {project_id}: {e}")

      codeowners_content = ""
      try:
        codeowners_paths = ["CODEOWNERS", ".github/CODEOWNERS", ".gitlab/CODEOWNERS", "docs/CODEOWNERS"]
        for path in codeowners_paths:
          try:
            codeowners_file = project.files.get(file_path=path, ref=project.default_branch)
            codeowners_content = base64.b64decode(codeowners_file.content).decode('utf-8', errors='replace')
            break
          except Exception as e:
            print(f"Error fetching CODEOWNERS at {path} for project ID {project_id}: {e}")
            continue
      except Exception as e:
        print(f"Error searching for CODEOWNERS for project ID {project_id}: {e}")


      repo_tags = []
      try:
        tags = project.tags.list(all=True)
        repo_tags = [tag.name for tag in tags]
      except Exception as e:
        print(f"Error fetching tags for project ID {project_id}: {e}")

      licenses_list = []
      try:
        if hasattr(project, 'license') and project.license:
          license_name = project.license.get("name", "")
          if license_name:
            licenses_list.append({
              "name": license_name,
              "URL": f"{project.web_url}/-/blob/{project.default_branch}/LICENSE"
            })
      except Exception as e:
        print(f"Error fetching license for project ID {project_id}: {e}")

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
        # "readme_content": readme_content,
        "_codeowners_content": codeowners_content,
        "_api_tags": repo_tags,
        "archived": project.archived
      }
    except Exception as e:
      print(f"Error fetching repository metadata for project ID {project_id}: {e}")
      return {}
