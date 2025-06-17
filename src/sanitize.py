from datetime import datetime
from github.GithubException import UnknownObjectException

class Sanitizer:
  def __init__(self):
    pass

  def get_repository_metadata(self, repo) -> str:
    if repo.fork:
      print(f"Skipping forked repository: {repo.full_name}")
      return None

    try:
      created_at_iso = repo.created_at.isoformat() if repo.created_at else ""
      pushed_at_iso = repo.pushed_at.isoformat() if repo.pushed_at else ""
      repo_visibility = "private" if repo.private else "public"
      languages = []
      try:
        lang_dict = repo.get_languages()
        if lang_dict:
          languages = list(lang_dict.keys())
      except Exception as e:
        print(f"Error fetching languages for {repo.full_name}: {e}")

      licenses = []
      if repo.license:
        licenses.append({ "name": repo.license.name })
      if not licenses:
        licenses.append({
          "name": "Apache License 2.0",
          "URL": "https://www.apache.org/licenses/LICENSE-2.0"
        })

      readme_url = ""
      # readme_content = None
      try:
        readme = repo.get_readme()
        readme_url = readme.html_url
        # b = base64.b64decode(readme.content)
        # try:
        #   readme_content = b.decode('utf-8')
        # except UnicodeDecodeError:
        #   try:
        #     readme_content = b.decode('latin-1')
        #   except Exception:
        #     readme_content = b.decode('utf-8', errors='ignore')
      except UnknownObjectException:
        pass
      except Exception as e:
        print(f"Error fetching README for {repo.name}: {e}")

      try:
        topics = repo.get_topics()
      except Exception:
        topics = []

      return {
        "name": repo.name,
        "description": repo.description or "",
        "organization": repo.owner.login,
        "repositoryURL": repo.html_url,
        "homepageURL": repo.homepage or repo.html_url,
        "vcs": "git",
        "repositoryVisibility": repo_visibility,
        "status": "development",
        "version": "N/A",
        "laborHours": 0,
        "languages": languages,
        "tags": topics,
        "date": {
          "created": created_at_iso,
          "lastModified": pushed_at_iso,
          "metadataLastUpdated": datetime.utcnow().isoformat()
        },
        "permissions": {
          "usageType": "",
          "exemptionText": "",
          "licenses": [{ "name": lic["name"] } for lic in licenses]
        },
        "contact": {
          "email": "",
          "name": "Centers for Disease Control and Prevention"
        },
        "repo_id": repo.id,
        "readme_url": readme_url,
        "privateID": str(repo.private)
      }
    except Exception as e:
      print(f"Failed processing repository {repo.full_name}: {e}")
      return None
