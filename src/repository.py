from github import Auth
from github import Github
from github import GithubIntegration

class Repository:

  def __init__(self, credentials=None):
    self.credentials = credentials

  def authenticate(self):
    app_id = self.credentials.get('github_app_id', '')
    installation_id = self.credentials.get('github_app_installation_id', '')
    private_key = self.credentials.get('github_app_private_key', '')

    ## Use the Github personal access token for authentication
    ## Otherwise, use GitHub App authentication
    ## This is just a personal preference, either is fine.
    if 'github_token' in self.credentials and self.credentials['github_token']:
      return Github(self.credentials['github_token'])
    auth = Auth.AppAuth(app_id, private_key)
    gi = GithubIntegration(auth=auth)
    access_token = gi.get_access_token(installation_id).token
    return Github(access_token)

  def get_repos(self):
    g = self.authenticate()
    org_name = self.credentials.get('github_org')
    org = g.get_organization(org_name)
    repos = list(
      org.get_repos(type='all')
    )
    print(f"Found {len(repos)} repositories in Github.com organization {org_name}")
    return repos

  def get_repo_by_id(self, repo_id):
    g = self.authenticate(self.credentials)
    try:
      repo = g.get_repo(int(repo_id))
      return repo
    except Exception as e:
      print(f"Repository with id {repo_id} not found: {e}")
      return None
