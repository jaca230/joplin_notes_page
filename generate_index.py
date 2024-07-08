import os

# Define the directory containing your HTML files
work_logs_dir = "Work Logs"
index_file_path = "index.html"

# Get a list of all HTML files in the directory
html_files = [f for f in os.listdir(work_logs_dir) if f.endswith(".html")]

# Start creating the content for the index file
html_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Index of Work Logs</title>
</head>
<body>
    <h1>Index of Work Logs</h1>
    <ul>
"""

# Add each HTML file to the index content as a link
for html_file in html_files:
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
