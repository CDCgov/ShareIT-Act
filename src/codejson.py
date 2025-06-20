class CodeJson:
  def get_header(self):
    header = {
      "version": "2.0",
      "agency": "CDC",
      "measurementType": {
        "method": "projects"
      }
    }
    return header

  def get_required_project_fields(self):
    required_fields = {
      "name": "",
      "description": "",
      "organization": "",
      "repositoryURL": "",
      "repositoryVisibility": "",
      "permissions": {
        "usageType": "",
        "exemptionText": "",
        "licenses": [
          {
            "name": ""
          }
        ]
      }
    }
    return required_fields

  def get_all_project_fields(self):
    all_fields = {
      "name": "",
      "description": "",
      "organization": "",
      "repositoryURL": "",
      "homepageURL": "",
      "vcs": "",
      "repositoryVisibility": "",
      "status": "",
      "version": "",
      "laborHours": 0,
      "languages": [],
      "tags": [],
      "date": {
        "created": "",
        "lastModified": "",
        "metadataLastUpdated": "",
      },
      "permissions": {
        "usageType": "",
        "exemptionText": "",
        "licenses": [
          {
            "name": ""
          }
        ]
      },
      "contact": {
        "email": "",
        "name": ""
      },
      "repo_id": 0,
      "readme_url": "",
      "privateID": ""
    }
    return all_fields
