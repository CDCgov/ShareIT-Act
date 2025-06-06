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
- A `code.json` file conforming to Federal Source Code Policy and SHARE IT Act metadata standards.
  The script assumes this file is in the same directory by default, but an alternative path can be
  specified via the command line.

📤 Output:
- An HTML file (e.g., `index.html` by default) containing an interactive table
  of metadata records. This table allows users to:
    - Sort data by any column.
    - Search/filter records dynamically.
    - Click direct links to repository URLs and approximate locations within the input `code.json` file (on GitHub).

✅ How to Use:
To run the script from the command line:
  Execute the script with: `python generate_reviewHTML.py [input__code_json_file] [-o output_html_file]`
     -  `[input__code_json_file]` (optional): Path to the `code.json` file. Defaults to `catalog/code.json`.
     -  `-o output_html_file` or `--output output_html_file` (optional): Specifies the output HTML file.
        Defaults to `docs/index.html`.
        
 ==> EXAMPLE:  python generate_reviewHTML.py
or ==> python generate_reviewHTML.py catalog/code.json -o docs/index.html


Author: CDC OCIO Support (Share IT Act Implementation)
"""
import json
import pandas as pd
from pathlib import Path
import html # Import the html module for escaping
import argparse
from typing import List, Dict, Any
import os

def analyze_json_structure(json_data):
    """
    Analyzes the structure of the JSON data to help understand its schema.
    Uses measurementType.method to determine the key for repository entries.
    """
    print("=== JSON Structure Analysis ===")
    
    # Check top-level keys
    print(f"Top-level keys: {list(json_data.keys())}")
    
    # Look for the measurementType.method field to determine the key for repository entries
    releases_key = None
    releases_data = None
    
    if 'measurementType' in json_data and isinstance(json_data['measurementType'], dict) and 'method' in json_data['measurementType']:
        releases_key = json_data['measurementType']['method']
        print(f"Found repository list key from measurementType.method: '{releases_key}'")
        
        if releases_key in json_data and isinstance(json_data[releases_key], list):
            releases_data = json_data[releases_key]
            print(f"Found {len(releases_data)} items under key: '{releases_key}'")
        else:
            print(f"Warning: Key '{releases_key}' from measurementType.method not found in data or is not a list")
    
    # Fallback to direct array if no measurementType.method or if the key wasn't found
    if not releases_key and isinstance(json_data, list):
        releases_data = json_data
        print(f"JSON appears to be a direct array with {len(releases_data)} items")
    
    # If we found a list of repositories, analyze the first one
    if releases_data and len(releases_data) > 0:
        sample = releases_data[0]        
        field_mapping = {}
        
        # Check for repository name
        for name_field in ['name', 'repositoryName', 'repo_name', 'title', 'project']:
            if name_field in sample:
                field_mapping['Repository Name'] = name_field
                break
        
        # Check for organization - the primary field name to look for is "organization".
        # The actual fallback to 'agency' is handled in generate_html_table.
        if 'organization' in sample:
            field_mapping['Organization'] = 'organization'
                
        # Check for contact information
        if 'contact' in sample:
            if isinstance(sample['contact'], dict) and 'email' in sample['contact']:
                field_mapping['Contact Email'] = 'contact.email'
            else:
                field_mapping['Contact Email'] = 'contact'
        elif 'email' in sample: # This was part of contact, but if exemption is removed, ensure correct indentation
            field_mapping['Contact Email'] = 'email'
            
        # Check for URL
        for url_field in ['repositoryURL', 'repository_url', 'url', 'homepage', 'repoURL']:
            if url_field in sample:
                field_mapping['Repository URL'] = url_field
                break
                
        # Check for version - only look for 'version'
        if 'version' in sample:
            field_mapping['Version'] = 'version'
                
        # Check for status - only look for 'status'
        if 'status' in sample:
            field_mapping['Status'] = 'status'
        
#        print("Suggested field mapping:")
#        pprint.pprint(field_mapping)
        
        return releases_key, field_mapping
    
    return None, {}

def find_entry_line_number(code_json_path, entry_identifier):
    """
    Find the actual line number for a specific entry in the code.json file.
    
    Args:
        code_json_path: Path to the code.json file
        entry_identifier: A unique identifier for the entry (e.g., repository name or URL)
        
    Returns:
        The approximate line number where the entry starts
    """
    try:
        with open(code_json_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
        # Convert the identifier to a string for comparison
        identifier_str = str(entry_identifier).strip()
        
        for i, line in enumerate(lines):
            # Look for lines containing the identifier
            if identifier_str in line:
                # Find the start of the entry (look for opening brace or bracket)
                start_line = i
                while start_line > 0:
                    if '{' in lines[start_line] and ('"name"' in lines[start_line+1] or '"repositoryName"' in lines[start_line+1]):
                        return start_line + 1  # Return the line number (1-indexed for GitHub)
                    start_line -= 1
                
                # If we couldn't find the start, return the line with the identifier
                return i + 1  # GitHub uses 1-indexed line numbers
                
        # If not found, return a default
        return 1
    except Exception as e:
        print(f"Error finding line number: {e}")
        return 1

def get_nested_value(data, path):
    """
    Gets a value from a nested dictionary using a dot-separated path.
    Example: get_nested_value(data, 'contact.email')
    """
    if '.' not in path:
        return data.get(path, "")
    
    parts = path.split('.')
    current = data
    for part in parts:
        if isinstance(current, dict) and part in current:
            current = current[part]
        else:
            return ""
    return current

def generate_html_table(code_json_path: Path, output_html_path: Path) -> None:
    """
    Reads a code.json file, extracts release information, and generates an HTML table.
    """
    try:
        # Check if the file exists
        if not os.path.exists(code_json_path):
            print(f"❌ Error: Input file not found at {code_json_path}")
            print(f"Current working directory: {os.getcwd()}")
            print(f"Absolute path attempted: {os.path.abspath(code_json_path)}")
            return
            
        with open(code_json_path, "r", encoding="utf-8") as f:
            code_data = json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: Input file not found at {code_json_path}")
        return
    except json.JSONDecodeError:
        print(f"❌ Error: Could not decode JSON from {code_json_path}. Please ensure it's valid JSON.")
        return

    # Analyze the JSON structure to understand the schema
    releases_key, field_mapping = analyze_json_structure(code_data)
    
    # Extract releases based on the analysis
    if releases_key and releases_key in code_data:
        releases = code_data[releases_key]
    elif isinstance(code_data, list):
        releases = code_data
    else:
        # If we couldn't determine the structure, fall back to the original approach
        releases = code_data.get("releases", [])
    
    if not releases:
        print("ℹ️ No releases found in the code.json file.")
        # Create an empty HTML file or handle as preferred
        output_html_path.parent.mkdir(parents=True, exist_ok=True)
        empty_html_content = create_html_document("<tbody><tr><td colspan='10'>No data available.</td></tr></tbody>")
        output_html_path.write_text(empty_html_content, encoding="utf-8")
        print(f"✅ Empty HTML table generated: {output_html_path}")
        return

    # Generate preview entries
    table_data: List[Dict[str, str]] = []
    
    for release in releases:
        # Use the field mapping from our analysis, or fall back to defaults
        repo_name = str(get_nested_value(release, field_mapping.get('Repository Name', 'name')))
        
        # Determine Organization value:
        # 1. Try the 'organization' field.
        # 2. If 'organization' is empty or not found, try the 'agency' field.
        org = str(get_nested_value(release, 'organization')) # Attempt to get from 'organization' field first
        if not org: # If the value from 'organization' field is empty
            org = str(get_nested_value(release, 'agency')) # Fallback to 'agency' field
        
        # Handle contact email which might be nested
        contact_path = field_mapping.get('Contact Email', 'contact.email')
        if contact_path == 'contact.email':
            contact = str(get_nested_value(release, contact_path))
        else:
            contact = str(get_nested_value(release, contact_path))
        
        # Determine Exemption value based on new rules
        exemption_value_to_display = "" # Initialize with empty string
        usage_type_str = "" 

        # Attempt to get value from permissions.usageType
        permissions_data = release.get('permissions')
 
        if isinstance(permissions_data, dict):
            usage_type = permissions_data.get('usageType')
            if usage_type is not None: # Check if 'usageType' key actually exists
                usage_type_str = str(usage_type)
                if usage_type_str not in ["governmentWideReuse", "openSource"]:
                    exemption_value_to_display = usage_type_str
        # If not processed_via_usage_type (i.e., permissions.usageType was not found or not applicable),
        # exemption_value_to_display will remain "", which is the desired behavior.

        # Determine if Public (Y/N)
        is_public_value = "N" # Default to No (Private)

        # First, check based on usageType
        if usage_type_str == "openSource":
            is_public_value = "Y"

        # Then, check based on repositoryURL content; this can make it Public even if not "openSource"
        # Determine Platform based on repositoryURL
        platform = "Unknown"
        url = str(get_nested_value(release, field_mapping.get('Repository URL', 'repositoryURL')))
        # Second, check based on repositoryURL content; this can make it Public even if not "openSource"
        if 'ShareIT-Act/assets/' not in url: # Check the original URL string
            is_public_value = "Y"
        repo_url_lower = url.lower()
        if "github.com" in repo_url_lower:
            platform = "GitHub"
        elif "gitlab.com" in repo_url_lower:
            platform = "GitLab"
        elif "dev.azure.com" in repo_url_lower or ".visualstudio.com" in repo_url_lower: # ADO can have older URLs too
            platform = "ADO"
        
        version = str(get_nested_value(release, field_mapping.get('Version', 'version')))
        status = str(get_nested_value(release, field_mapping.get('Status', 'status')))

        # Escape values for use in HTML title attributes
        escaped_repo_name = html.escape(repo_name)
        escaped_org = html.escape(org)

        # GitHub link to approximate location in code.json
        code_link_path = code_json_path.name # Default to just the filename if not in a known repo structure
        if "catalog/code.json" in str(code_json_path).replace("\\", "/"): # Make path comparison OS-agnostic
            code_link_path = "catalog/code.json" 

        # Find the actual line number for this entry
        repo_identifier = repo_name or url  # Use repository name or URL as identifier
        line_number = find_entry_line_number(code_json_path, repo_identifier)
        code_link_url = f"https://github.com/CDCgov/ShareIT-Act/blob/main/{code_link_path}#L{line_number}"
        
        table_data.append({
            "Repository Name": f'<span title="{escaped_repo_name}">{repo_name}</span>', # Wrap in span with title
            "Organization": f'<span title="{escaped_org}">{org}</span>',         # Wrap in span with title
            "Contact Email": contact,
            "Exemption": exemption_value_to_display,
            "Public": is_public_value,
            "Platform": platform,
            "Repository URL": f'<a href="{url}" target="_blank">{url}</a>' if url.startswith("http") else url,
            "Version": version,
            "Status": status,
            "View in code.json": f'<a href="{code_link_url}" target="_blank">View (L{line_number})</a>'
        })

    # Convert to DataFrame and sort
    df = pd.DataFrame(table_data)
    if not df.empty:
        df = df.sort_values(by=["Organization", "Repository Name"])

    # Generate HTML table from DataFrame
    # We pre-formatted links, so escape=False is needed.
    # index=False to avoid writing DataFrame index.
    table_html = df.to_html(escape=False, index=False, table_id="metadataTable", classes="display", border=0)
    
    full_html_content = create_html_document(table_html)

    # Save to output file
    output_html_path.parent.mkdir(parents=True, exist_ok=True) # Ensure directory exists
    output_html_path.write_text(full_html_content, encoding="utf-8")
    print(f"✅ HTML table generated: {output_html_path}")

def create_html_document(table_html_content: str) -> str:
    """Creates the full HTML document string with DataTables integration."""
    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>CDC Metadata Preview Table</title>
        <link rel="stylesheet" href="https://cdn.datatables.net/1.13.6/css/jquery.dataTables.css">
        <script src="https://code.jquery.com/jquery-3.7.1.min.js"></script>
        <script src="https://cdn.datatables.net/1.13.6/js/jquery.dataTables.min.js"></script>
        <style>
            body {{ font-family: sans-serif; margin: 20px; }}
            table.dataTable th, table.dataTable td {{ padding: 8px; vertical-align: top; }} /* Added vertical-align */
            table.dataTable th {{ background-color: #f2f2f2; }}
            /* Set minimum width and no wrap for the Repository Name column (1st column) */
            table.dataTable th:nth-child(1),
            table.dataTable td:nth-child(1) {{
                min-width: 10ch; /* Minimum width for 10 characters */
                white-space: nowrap; /* Prevent text wrapping */
            }}
            /* Set minimum width for the Organization column (2nd column) */
            table.dataTable th:nth-child(2),
            table.dataTable td:nth-child(2) {{
                min-width: 30ch;
            }}
        </style>
        <script>
            $(document).ready(function () {{
                $('#metadataTable').DataTable({{
                    "pageLength": 100,  // Increased from 25 to 100
                    "lengthMenu": [10, 25, 50, 100, 250, 500, 1000, -1],  // Add option for "All" (-1)
                    "lengthChange": true  // Ensure the dropdown is visible
                }});
            }});
        </script>
    </head>
    <body>
        <h2>CDC Share IT Act - Metadata Preview Table</h2>
        <p>This table supports filtering, sorting, and links to the <code>code.json</code> source. 
        The "View in code.json" link points to the line number on GitHub.</p>
        {table_html_content}
        <p><small>Showing <span id="entry-count">0</span> of <span id="total-count">0</span> entries</small></p>
        <script>
            // Add a counter to show how many entries are displayed vs. total
            $(document).ready(function() {{
                var table = $('#metadataTable').DataTable();
                $('#total-count').text(table.data().count());
                
                table.on('draw', function() {{
                    $('#entry-count').text(table.page.info().recordsDisplay);
                }});
                
                // Trigger initial count
                $('#entry-count').text(table.page.info().recordsDisplay);
            }});
        </script>
    </body>
    </html>
    """

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an HTML preview table from a code.json file.")
    parser.add_argument(
        "input_file",
        type=Path,
        nargs="?", # Makes the argument optional
        default=Path("catalog/code.json"),
        help="Path to the input code.json file (default: catalog/code.json)"
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("docs/index.html"),
        help="Path to the output HTML file (default: docs/index.html)"
    )
    args = parser.parse_args()

    generate_html_table(args.input_file, args.output)
