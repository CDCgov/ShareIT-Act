from github import Auth
from github import Github
from github import GithubIntegration

class Repository:
  def __init__(self, org):
    self.org = org

  def authenticate(self, credentials):
    auth = Auth.AppAuth(credentials.app_id, credentials.private_key)
    gi = GithubIntegration(auth=auth)
    g = gi.get_github_for_installation(credentials.installation_id, credentials.token_permissions)
    return g

  def get_repos(self, credentials):
    g = self.authenticate(credentials)
    repos = []
    for repo in g.get_organization('cdcent').get_repos(type='all'):
      print(repo.name)
      print(repo.html_url)
      print(repo.description)
      print(repo.created_at)
      print(repo.updated_at)
      print(repo.pushed_at)
      print(repo.language)
      print(repo.size)
      print(repo.stargazers_count)
      print(repo.forks_count)
      print(repo.open_issues_count)
      print(repo.watchers_count)
      print(repo.default_branch)
      print(repo.has_issues)
      print(repo.has_wiki)
      print(repo.has_downloads)
      repos.append(repo)
    return repos
