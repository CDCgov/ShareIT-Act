from github import Auth
from github import GithubIntegration

class Repository:
  def authenticate(self, credentials):
    auth = Auth.AppAuth(credentials.get('github_app_id'), credentials.get('github_app_private_key'))
    gi = GithubIntegration(auth=auth)
    g = gi.get_github_for_installation(credentials.get('github_app_installation_id'))
    return g

  def get_repos(self, credentials):
    g = self.authenticate(credentials)
    repos = []
    for repo in g.get_organization(credentials.get('github_org')).get_repos(type='all'):
      repos.append(repo)
    return repos
