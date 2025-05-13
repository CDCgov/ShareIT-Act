"""
CDC Share IT Act – Metadata Review HTML Generator
--------------------------------------------------

This script reads a `code.json` metadata file (structured according to the Federal Source Code Policy and SHARE IT Act),
extracts key fields from each repository entry, and generates a human-readable HTML table.

📌 Purpose:
- To help C/I/Os, ADIs, and project teams review their entries during the preview period.
- To simplify validation of repository metadata without manually searching a raw JSON file.

📥 Input:
- A valid `code.json` file (must include a "releases" array).

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

# Load code.json file
catalog_path = Path("catalog/code.json")
with open(catalog_path, "r") as f:
    code_data = json.load(f)

# Extract releases
releases = code_data.get("releases", [])

# Generate preview entries
table_data = []
line_number = 10  # approximate starting line
for release in releases:
    repo_name = release.get("name", "")
    org = release.get("organization", "")
    contact = release.get("contact", {}).get("email", "")
    exemption = release.get("permissions", {}).get("exemption", "")
    url = release.get("repositoryURL", "")
    version = release.get("version", "")
    status = release.get("status", "")

    # GitHub link to approximate location in code.json
    code_link = f"https://github.com/CDCgov/ShareIT-Act/blob/main/catalog/code.json#L{line_number}"
    table_data.append({
        "Repository Name": repo_name,
        "Organization": org,
        "Contact Email": contact,
        "Exemption": exemption,
        "Repository URL": url,
        "Version": version,
        "Status": status,
        "View in code.json": code_link
    })

    line_number += 20  # assume ~20 lines per entry

# Convert to DataFrame and sort
df = pd.DataFrame(table_data)
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
