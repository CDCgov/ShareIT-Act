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

# Load the code.json file
with open("code.json", "r") as f:
    code_data = json.load(f)

# Flatten and extract the list of custom-developed software entries
df = pd.json_normalize(code_data["releases"])

# Select fields of interest
selected_fields = [
    "name",
    "organization",
    "contact.email",
    "permissions.exemption",
    "repositoryURL",
    "version",
    "status"
]

# Filter to fields that actually exist in the data
selected_fields = [field for field in selected_fields if field in df.columns]
df_preview = df[selected_fields].fillna("")

# Rename columns for clarity
df_preview.columns = [
    "Repository Name",
    "Organization",
    "Contact Email",
    "Exemption",
    "Repository URL",
    "Version",
    "Status"
][:len(df_preview.columns)]

# Export to an HTML table
html_output_path = "metadata_preview_table.html"
df_preview.to_html(html_output_path, index=False, escape=False, render_links=True)

print(f"✅ Preview HTML generated at: {html_output_path}")
