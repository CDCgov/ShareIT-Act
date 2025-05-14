"""
CDC Share IT Act – Metadata Review HTML Generator
--------------------------------------------------

This script reads a `code.json` metadata file (structured according to the Federal Source Code Policy and SHARE IT Act),
extracts key fields from each repository entry, and generates a human-readable HTML table.

📌 Purpose:
- This tool is designed for C/I/Os, ADIs, and project teams involved in the CDC's implementation of the
  Federal Source Code Policy and the SHARE IT Act. It simplifies the review and validation of software
  metadata entries by presenting the information in an easily navigable HTML table, rather than
  requiring manual inspection of a raw JSON file. This is particularly useful during preview periods
  when ensuring data accuracy.

📥 Input:
- A `code.json` file conforming to Federal Source Code Policy and SHARE IT Act metadata standards
  (must include a "releases" array). The script assumes this file is in the same directory by default,
  but an alternative path can be specified via the command line.

📤 Output:
- A file named `metadata_preview_table.html` with searchable and clickable metadata records.

✅ How to Use:
1. Place this script in the same folder as your `code.json` file.
2. Run the script using Python 3.
3. Open `metadata_preview_table.html` in any browser to review entries.

Author: CDC OCIO Support (Share IT Act Implementation)
"""
import json
import pandas as pd
from pathlib import Path
import argparse
from typing import List, Dict, Any

def generate_html_table(code_json_path: Path, output_html_path: Path) -> None:
    """
    Reads a code.json file, extracts release information, and generates an HTML table.
    """
    try:
        with open(code_json_path, "r", encoding="utf-8") as f:
            code_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Input file not found at {code_json_path}")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: Could not decode JSON from {code_json_path}. Please ensure it's valid JSON.")
        return

    # Extract releases
    releases: List[Dict[str, Any]] = code_data.get("releases", [])
    if not releases:
        print("ℹ️ No releases found in the code.json file.")
        # Create an empty HTML file or handle as preferred
        output_html_path.parent.mkdir(parents=True, exist_ok=True)
        empty_html_content = create_html_document("<tbody><tr><td colspan='8'>No data available.</td></tr></tbody>")
        output_html_path.write_text(empty_html_content, encoding="utf-8")
        print(f"✅ Empty HTML table generated: {output_html_path}")
        return

    # Generate preview entries
    table_data: List[Dict[str, str]] = []
    line_number = 10  # approximate starting line for GitHub links
    for release in releases:
        repo_name = str(release.get("name", ""))
        org = str(release.get("organization", ""))
        contact = str(release.get("contact", {}).get("email", ""))
        exemption = str(release.get("permissions", {}).get("exemption", ""))
        url = str(release.get("repositoryURL", ""))
        version = str(release.get("version", ""))
        status = str(release.get("status", ""))

        # GitHub link to approximate location in code.json
        # Note: This line number is an approximation.
        # For a more accurate link, the source code.json would need to be on GitHub
        # and the path adjusted accordingly.
        # Assuming the input code.json is the one in `CDCgov/ShareIT-Act/catalog/code.json`
        # If using a local file not in that repo, this link might not be relevant or correct.
        # Consider making the base GitHub URL configurable if this script is used with other code.json files.
        code_link_path = code_json_path.name # Default to just the filename if not in a known repo structure
        if "catalog/code.json" in str(code_json_path).replace("\\", "/"): # Make path comparison OS-agnostic
            code_link_path = "catalog/code.json" # Or derive more accurately if possible

        code_link_url = f"https://github.com/CDCgov/ShareIT-Act/blob/main/{code_link_path}#L{line_number}"
        
        table_data.append({
            "Repository Name": repo_name,
            "Organization": org,
            "Contact Email": contact,
            "Exemption": exemption,
            "Repository URL": f'<a href="{url}" target="_blank">{url}</a>' if url.startswith("http") else url,
            "Version": version,
            "Status": status,
            "View in code.json": f'<a href="{code_link_url}" target="_blank">View (approx. L{line_number})</a>'
        })
        line_number += 20  # assume ~20 lines per entry; this remains an approximation

    # Convert to DataFrame and sort
    df = pd.DataFrame(table_data)
    if not df.empty:
        df = df.sort_values(by=["Organization", "Repository Name"])

# Create interactive HTML using DataTables
html = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>CDC Metadata Preview Table</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.css">
    <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
    <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready(function () {
            $('#metadataTable').DataTable();
        });
    </script>
</head>
<body>
    <h2>CDC Share IT Act - Metadata Preview Table</h2>
    <p>This table supports filtering, sorting, and links to the <code>code.json</code> source.</p>
    <table id="metadataTable" class="display" style="width:100%">
        <thead>
            <tr>
"""

# Add table headers
for col in df.columns:
    html += f"<th>{col}</th>\n"

html += "</tr></thead>\n<tbody>\n"

# Add table rows
for _, row in df.iterrows():
    html += "<tr>\n"
    for col in df.columns:
        value = row[col]
        if col == "View in code.json":
            html += f'<td><a href="{value}" target="_blank">View</a></td>\n'
        elif isinstance(value, str) and value.startswith("http"):
            html += f'<td><a href="{value}" target="_blank">{value}</a></td>\n'
        else:
            html += f"<td>{value}</td>\n"
    html += "</tr>\n"

html += "</tbody></table></body></html>"

# Save to /interactive
output_dir = Path("interactive")
output_dir.mkdir(exist_ok=True)
output_file = output_dir / "metadata_preview_table.html"
output_file.write_text(html)

print(f"✅ HTML table generated: {output_file}")
