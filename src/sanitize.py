import base64

from datetime import datetime, timezone
from github.GithubException import UnknownObjectException
from src.inference import Inference

class Sanitizer:

  def get_file_content(self, repo, file_path):
    """
    A best effort approach to fetch and decodes the content of a file from the repository.
    If there's no data, or if the file is not found, it returns None.

    Args:
        repo: The PyGithub Repository object.
        file_path: The path to the file in the repository (e.g., 'README.md').

    Returns:
        The decoded file content as a string, or None if not found or on error.
    """
    try:
      content_item = repo.get_contents(file_path)
      return base64.b64decode(content_item.content).decode('utf-8', errors='ignore')
    except UnknownObjectException:
      return None  # File not found is a normal case
    except Exception as e:
      print(f"Error fetching '{file_path}' for {repo.full_name}: {e}")
      return None

  def get_repository_metadata(self, repo) -> str:
    if repo.fork:
      print(f"Skipping forked repository: {repo.full_name}")
      return None

    # Skip empty repositories to avoid errors when fetching contents.
    if repo.size == 0:
      print(f"Skipping empty repository: {repo.full_name}")
      return None

    try:
      inference = Inference()
      readme_content = self.get_file_content(repo, 'README.md')
      codeowners_content = self.get_file_content(repo, 'CODEOWNERS')

      languages = list(repo.get_languages().keys())
      usage_type, exemption_text, repository_url = inference.infer_usage_and_url(
        repo.private,
        repo.license,
        repo.html_url,
        readme_content,
        languages)
      status = inference.infer_status(repo.archived, repo.pushed_at, readme_content)
      organization = inference.infer_organization(repo.name, readme_content)
      contact_email = inference.infer_contact_email(repo.private, readme_content, codeowners_content)
      version = inference.infer_version(repo.get_tags(), readme_content)

      # --- Assemble the final metadata object ---
      metadata = {
        "name": repo.name,
        "organization": organization,
        "description": repo.description or "",
        "version": version,
        "laborHours": 0,
        "status": status,
        "vcs": "git",
        "homepageURL": repo.homepage or "",
        "repositoryURL": repository_url,
        "repositoryVisibility": "private" if repo.private else "public",
        "languages": languages,
        "tags": repo.get_topics(),
        "contact": {
          "email": contact_email
        },
        "date": {
          "created": repo.created_at.isoformat(),
          "lastModified": repo.pushed_at.isoformat(),
          "metadataLastUpdated": datetime.now(timezone.utc).isoformat()
        },
        "permissions": {
          "usageType": usage_type,
          "licenses": [{"name": repo.license.name}] if repo.license else []
        },
        "repo_id": repo.id,
        "private_id": f"github_{repo.id}",
        "_url": repo.html_url
      }

      if exemption_text:
        metadata["permissions"]["exemptionText"] = exemption_text

      return metadata

    except Exception as e:
      print(f"Failed processing repository {repo.full_name}: {e}")
      return None
