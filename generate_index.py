import os
import re
from datetime import datetime
from PyPDF2 import PdfReader

# Define the directories
work_logs_dir = "Work Logs"
presentations_dir = "Presentations"
index_file_path = "index.html"
presentations_file_path = "presentations.html"

# Regular expression to match date in the format dd_mm_yyyy
date_pattern = re.compile(r"(\d{2}_\d{2}_\d{4})")

# Function to parse date from filename
def parse_date_from_filename(filename):
    match = date_pattern.search(filename)
    if match:
        return datetime.strptime(match.group(1), "%d_%m_%Y")
    return None

# Function to parse date from the last part of the PDF filename
def parse_date_from_pdf_filename(pdf_filename):
    date_time_str = pdf_filename[-23:-4]  # Extract 'yyyy-mm-dd-hh-mm-ss'
    try:
        return datetime.strptime(date_time_str, "%Y-%m-%d_%H-%M-%S")
    except ValueError:
        return None

# Function to get the number of slides in a PDF file
def get_number_of_slides(pdf_file_path):
    try:
        with open(pdf_file_path, "rb") as pdf_file:
            reader = PdfReader(pdf_file)
            return len(reader.pages)
    except Exception as e:
        print(f"Error reading {pdf_file_path}: {e}")
        return 0

# Get a list of all HTML files in the directory
html_files = [f for f in os.listdir(work_logs_dir) if f.endswith(".html")]

# Separate HTML files into those with valid dates and those without
dated_files = []
other_files = []

for html_file in html_files:
    file_date = parse_date_from_filename(html_file)
    if file_date:
        dated_files.append((file_date, html_file))
    else:
        other_files.append(html_file)

# Sort the dated HTML files by date (newest first)
dated_files.sort(key=lambda x: x[0], reverse=True)

# Get a list of all presentation PDFs
presentation_files = [f for f in os.listdir(presentations_dir) if f.endswith(".pdf")]
presentations = []

# Process PDF files to get creation dates and slide counts
for pdf_file in presentation_files:
    creation_date = parse_date_from_pdf_filename(pdf_file)
    num_slides = get_number_of_slides(os.path.join(presentations_dir, pdf_file))
    if creation_date:
        presentations.append((creation_date, pdf_file, num_slides))
    else:
        print(f"Failed to extract date from PDF: {pdf_file}")

# Sort presentations by date (newest first)
presentations.sort(key=lambda x: x[0], reverse=True)

# Generate Work Logs index.html
html_content_work_logs = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jack Carlton's Work Logs</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.10.24/css/jquery.dataTables.min.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            color: #343a40;
            margin: 20px;
        }
        .navbar {
            overflow: hidden;
            background-color: #007bff;
            padding: 8px 20px;
        }
        .navbar a {
            float: left;
            color: white;
            text-align: center;
            padding: 12px 16px;
            text-decoration: none;
        }
        .navbar a:hover {
            background-color: #0056b3;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border: 1px solid #dee2e6;
        }
        th {
            background-color: #007bff;
            color: white;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="index.html">Work Logs</a>
        <a href="presentations.html">Presentations</a>
    </div>

    <h2>Work Logs</h2>
    <table id="workLogsDataTable">
        <thead>
            <tr>
                <th>File Name</th>
                <th>Creation Date</th>
            </tr>
        </thead>
        <tbody>
"""

for file_date, html_file in dated_files:
    html_content_work_logs += f'            <tr><td><a href="{work_logs_dir}/{html_file}">{html_file}</a></td><td>{file_date.strftime("%Y-%m-%d")}</td></tr>\n'

if other_files:
    for html_file in other_files:
        html_content_work_logs += f'            <tr><td><a href="{work_logs_dir}/{html_file}">{html_file}</a></td><td>Unknown</td></tr>\n'

html_content_work_logs += """
        </tbody>
    </table>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready(function() {
            $('#workLogsDataTable').DataTable({
                "order": [[1, "desc"]]  // Default sort by newest date
            });
        });
    </script>
</body>
</html>
"""

with open(index_file_path, "w") as index_file:
    index_file.write(html_content_work_logs)

# Generate Presentations presentations.html
html_content_presentations = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Jack Carlton's Presentations</title>
    <link rel="stylesheet" href="https://cdn.datatables.net/1.10.24/css/jquery.dataTables.min.css">
    <style>
        body {
            font-family: Arial, sans-serif;
            background-color: #f8f9fa;
            color: #343a40;
            margin: 20px;
        }
        .navbar {
            overflow: hidden;
            background-color: #007bff;
            padding: 8px 20px;
        }
        .navbar a {
            float: left;
            color: white;
            text-align: center;
            padding: 12px 16px;
            text-decoration: none;
        }
        .navbar a:hover {
            background-color: #0056b3;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-bottom: 20px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border: 1px solid #dee2e6;
        }
        th {
            background-color: #007bff;
            color: white;
        }
    </style>
</head>
<body>
    <div class="navbar">
        <a href="index.html">Work Logs</a>
        <a href="presentations.html">Presentations</a>
    </div>

    <h2>Presentations</h2>
    <table id="presentationsDataTable">
        <thead>
            <tr>
                <th>File Name</th>
                <th>Slides</th>
                <th>Creation Date</th>
            </tr>
        </thead>
        <tbody>
"""

for creation_date, pdf_file, num_slides in presentations:
    display_name = pdf_file[:-24] if len(pdf_file) > 23 else pdf_file
    html_content_presentations += f'            <tr><td><a href="{presentations_dir}/{pdf_file}">{display_name}</a></td><td>{num_slides}</td><td>{creation_date.strftime("%Y-%m-%d")}</td></tr>\n'

html_content_presentations += """
        </tbody>
    </table>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script src="https://cdn.datatables.net/1.10.24/js/jquery.dataTables.min.js"></script>
    <script>
        $(document).ready(function() {
            $('#presentationsDataTable').DataTable({
                "order": [[2, "desc"]]  // Default sort by newest date
            });
        });
    </script>
</body>
</html>
"""

with open(presentations_file_path, "w") as presentations_file:
    presentations_file.write(html_content_presentations)

print("HTML files generated:")
print(f"- {index_file_path}")
print(f"- {presentations_file_path}")
