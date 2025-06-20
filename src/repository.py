from github import Auth
from github import Github
from github import GithubIntegration

class Repository:
  def authenticate(self, credentials):
    app_id = credentials.get('github_app_id', '')
    installation_id = credentials.get('github_app_installation_id', '')
    private_key = credentials.get('github_app_private_key', '')

    ## Use the Github personal access token for authentication
    ## Otherwise, use GitHub App authentication
    ## This is just a personal preference, either is fine.
    if 'github_token' in credentials and credentials['github_token']:
      return Github(credentials['github_token'])
    auth = Auth.AppAuth(app_id, private_key)
    gi = GithubIntegration(auth=auth)
    access_token = gi.get_access_token(installation_id).token
    return Github(access_token)

  def get_repos(self, credentials):
    g = self.authenticate(credentials)
    org_name = credentials.get('github_org')
    org = g.get_organization(org_name)
    repos = list(
      org.get_repos(type='all')
    )
    return repos
