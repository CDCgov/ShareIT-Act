import json

from datetime import datetime
from pathlib import Path

class Combine:

  ###########################################################
  ## We were asked to censor particular metadata information
  ## for code.json output based on certain criteria.
  ##
  ## 1. username being abc1 is no longer part of the email
  ## 2. internal URLs are no longer displayed.
  ##
  ##########################################################
  def censor_information(self, filename, repo):
    censored = dict(repo)
    if self.to_exclude_private_repository(filename, repo):
      censored.pop('_url', None)
      censored['contact'] = {}
      censored['contact']['email'] = "shareit@cdc.gov"
      censored['homepageURL'] = ""
      censored['repositoryURL'] = ""
    return censored

  def is_past_cutoff_date(self, cutoff_date, date):
    try:
      dt_cutoff = datetime.fromisoformat(cutoff_date.replace("Z", "+00:00"))
      dt_date = datetime.fromisoformat(date.replace("Z", "+00:00"))
      return dt_date < dt_cutoff
    except Exception as e:
      print(f"Could not parse date: {date} ({e})")
    return False

  def to_exclude_private_repository(self, filename, repo):
    if "ado" in filename.lower() or "gitlab" in filename.lower():
      return True
    if repo.get('repositoryVisibility', '').lower() == 'private':
      is_private = repo.get('repositoryVisibility', '').lower() == 'private'
      if is_private:
        return True
    return False

  ###########################################################
  ## We were asked to exclude certain repositories
  ## for code.json output based on certain criteria.
  ##
  ## 1. When including "private" repositories, only
  ## include repositories updated on or after June 21 2025.
  ## 2. Repositories that are in Gitlab or Azure Devops
  ## are hosted internal to CDC are considered "private".
  ## 3. Github Enterprise Cloud (github.com) repositories
  ## are considered public unless they are marked private
  ##
  ##########################################################
  def to_exclude_repository(self, filename, repo):
    if "ado" in filename.lower() or "gitlab" in filename.lower():
      last_modified = repo.get('date', {}).get('lastModified', '')
      if last_modified and self.is_past_cutoff_date("2025-06-21T00:00:00Z", last_modified):
        return True
      return False

    if repo.get('repositoryVisibility', '').lower() == 'private':
      last_modified = repo.get('date', {}).get('lastModified', '')
      is_private = repo.get('repositoryVisibility', '').lower() == 'private'
      if is_private:
        if last_modified and self.is_past_cutoff_date("2025-06-21T00:00:00Z", last_modified):
          return True
    return False

  def combine_json_files_with_public(self, input_dir, output_dir=None):
    raw_data_path = Path(input_dir)
    if not raw_data_path.exists() or not raw_data_path.is_dir():
      print(f"Directory not found: {raw_data_path}")
      return None

    print(f"Combining JSON files from {raw_data_path}")
    json_files = list(raw_data_path.glob('*.json'))
    if not json_files:
      print("No JSON files found")
      return None

    combined_data = []
    for file_path in json_files:
      print(f"Reading {file_path.name}")
      try:
        with open(file_path, 'r') as f:
          data = json.load(f)
          if not isinstance(data, list):
            print(f"Error: {file_path.name} does not contain a list of objects, skipping")
            continue
          for repo in data:
            to_exclude = self.to_exclude_private_repository(file_path.name, repo)
            if not to_exclude:
              if isinstance(repo, dict) and "description" not in repo:
                repo["description"] = ""
              combined_data.append(repo)

      except json.JSONDecodeError:
        print(f"Error: {file_path.name} is not valid JSON, skipping")
      except Exception as e:
        print(f"Error processing {file_path.name}: {e}")

    if not combined_data:
      print("No valid data found")
      return None

    output_path = Path(output_dir if output_dir else input_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "code.json"

    data = {
      "version": "2.0",
      "agency": "CDC",
      "measurementType": {
          "method": "projects"
      },
      "releases": combined_data
    }

    with open(output_file, 'w') as f:
      json.dump(data, f, indent=2)

    print(f"Combined data saved to {output_file}")
    print(f"Total repositories: {len(combined_data)}")
    return str(output_file)

  def combine_json_files_with_filter(self, input_dir, output_dir=None):
    raw_data_path = Path(input_dir)
    if not raw_data_path.exists() or not raw_data_path.is_dir():
      print(f"Directory not found: {raw_data_path}")
      return None

    print(f"Combining JSON files from {raw_data_path}")
    json_files = list(raw_data_path.glob('*.json'))
    if not json_files:
      print("No JSON files found")
      return None

    combined_data = []
    for file_path in json_files:
      print(f"Reading {file_path.name}")
      try:
        with open(file_path, 'r') as f:
          data = json.load(f)
          if not isinstance(data, list):
            print(f"Error: {file_path.name} does not contain a list of objects, skipping")
            continue
          for obj in data:
            to_exclude = self.to_exclude_repository(file_path.name, obj)
            censored = self.censor_information(file_path.name, obj)
            if not to_exclude:
              if "description" not in censored:
                censored["description"] = ""
              combined_data.append(censored)

      except json.JSONDecodeError:
        print(f"Error: {file_path.name} is not valid JSON, skipping")
      except Exception as e:
        print(f"Error processing {file_path.name}: {e}")

    if not combined_data:
      print("No valid data found")
      return None

    output_path = Path(output_dir if output_dir else input_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "code.json"

    data = {
      "version": "2.0",
      "agency": "CDC",
      "measurementType": {
          "method": "projects"
      },
      "releases": combined_data
    }

    with open(output_file, 'w') as f:
      json.dump(data, f, indent=2)

    print(f"Combined data saved to {output_file}")
    print(f"Total repositories: {len(combined_data)}")
    return str(output_file)

  def combine_json_files(self, input_dir, output_dir=None):
    raw_data_path = Path(input_dir)
    if not raw_data_path.exists() or not raw_data_path.is_dir():
      print(f"Directory not found: {raw_data_path}")
      return None

    print(f"Combining JSON files from {raw_data_path}")
    json_files = list(raw_data_path.glob('*.json'))
    if not json_files:
      print("No JSON files found")
      return None

    combined_data = []

    # We generate the code.json file based on a list of raw data files
    # with the expectation that each file contains a list of objects
    # If it doesn't meet this expectation, we skip the file and log an error
    for file_path in json_files:
      print(f"Reading {file_path.name}")
      try:
        with open(file_path, 'r') as f:
          data = json.load(f)
          if not isinstance(data, list):
            print(f"Error: {file_path.name} does not contain a list of objects, skipping")
            continue
          for obj in data:
            if isinstance(obj, dict) and "description" not in obj:
              obj["description"] = ""
            combined_data.append(obj)
      except json.JSONDecodeError:
        print(f"Error: {file_path.name} is not valid JSON, skipping")
      except Exception as e:
        print(f"Error processing {file_path.name}: {e}")

    if not combined_data:
      print("No valid data found")
      return None

    output_path = Path(output_dir if output_dir else input_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    output_file = output_path / "code.json"

    data = {
      "version": "2.0",
      "agency": "CDC",
      "measurementType": {
          "method": "projects"
      },
      "releases": combined_data
    }

    with open(output_file, 'w') as f:
      json.dump(data, f, indent=2)

    print(f"Combined data saved to {output_file}")
    print(f"Total repositories: {len(combined_data)}")
    return str(output_file)
