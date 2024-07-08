import os
import re
from datetime import datetime

# Define the directory containing your HTML files
work_logs_dir = "Work Logs"
index_file_path = "index.html"

# Regular expression to match date in the format dd_mm_yyyy
date_pattern = re.compile(r"(\d{2}_\d{2}_\d{4})")

# Function to parse date from filename
def parse_date_from_filename(filename):
    match = date_pattern.search(filename)
    if match:
        return datetime.strptime(match.group(1), "%d_%m_%Y")
    return None

# Get a list of all HTML files in the directory
html_files = [f for f in os.listdir(work_logs_dir) if f.endswith(".html")]

# Separate files into those with valid dates and those without
dated_files = []
other_files = []

for html_file in html_files:
    file_date = parse_date_from_filename(html_file)
    if file_date:
        dated_files.append((file_date, html_file))
    else:
        other_files.append(html_file)

# Sort the dated files by date (newest first)
dated_files.sort(key=lambda x: x[0], reverse=True)

# Start creating the content for the index file
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index of Work Logs</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            color: #343a40;
            margin: 20px;
            line-height: 1.6;
        }
        h1 {
            color: #007bff;
        }
        h2 {
            color: #495057;
        }
        ul {
            list-style-type: none;
            padding: 0;
        }
        li {
            margin: 8px 0;
            padding: 10px;
            background: #ffffff;
            border: 1px solid #dee2e6;
            border-radius: 4px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        a {
            text-decoration: none;
            color: #007bff;
        }
        a:hover {
            text-decoration: underline;
        }
    </style>
</head>
<body>
    <h1>Index of Work Logs</h1>
    <h2>Dated Entries</h2>
    <ul>
"""

# Add each dated HTML file to the index content as a link
for file_date, html_file in dated_files:
    html_content += f'        <li><a href="{work_logs_dir}/{html_file}">{html_file} ({file_date.strftime("%d %B %Y")})</a></li>\n'

# Add other files to the index content
if other_files:
    html_content += """
    </ul>
    <h2>Other Entries</h2>
    <ul>
"""
    for html_file in other_files:
        html_content += f'        <li><a href="{work_logs_dir}/{html_file}">{html_file}</a></li>\n'

# Close the HTML tags
html_content += """
    </ul>
</body>
</html>
"""

# Write the content to the index.html file
with open(index_file_path, "w") as index_file:
    index_file.write(html_content)

print(f"Index file created at {index_file_path}")
