import json

from pathlib import Path

class Combine:
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
    for file_path in json_files:
      print(f"Reading {file_path.name}")
      try:
        with open(file_path, 'r') as f:
          data = json.load(f)
          if isinstance(data, list):
            combined_data.extend(data)
          else:
            combined_data.append(data)
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
      "projects": combined_data
    }

    with open(output_file, 'w') as f:
      json.dump(data, f, indent=2)

    print(f"Combined data saved to {output_file}")
    print(f"Total repositories: {len(combined_data)}")
    return str(output_file)
