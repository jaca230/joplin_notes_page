import io
import argparse
import json
from datetime import datetime
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload

# If modifying these scopes, delete the token file that lives alongside this script.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parents[1]
PRESENTATIONS_DIR = REPO_ROOT / "public" / "resources" / "presentations"
TOKEN_PATH = SCRIPT_DIR / "token.json"
CREDENTIALS_PATH = SCRIPT_DIR / "credentials.json"


def create_folder_if_not_exists(folder_path: Path):
    """Create a folder if it doesn't already exist."""
    if not folder_path.exists():
        folder_path.mkdir(parents=True, exist_ok=True)
        print(f"Created folder: {folder_path}")


def download_file(file_id, destination_path: Path, service, mime_type, overwrite):
    """Download a file from Google Drive."""
    if destination_path.exists() and not overwrite:
        print(f"File already exists and overwrite is set to False: {destination_path}. Skipping download.")
        return
    
    if mime_type == 'application/vnd.google-apps.presentation':
        # Export Google Slides as a PDF file
        request = service.files().export_media(fileId=file_id, mimeType='application/pdf')
    else:
        # Regular download for other file types
        request = service.files().get_media(fileId=file_id)
        
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)

    done = False
    target_name = destination_path.name
    print(f"Starting download: {target_name}")
    try:
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}% complete for {target_name}.")
    except HttpError as error:
        if _is_export_size_limit_error(error):
            print(
                f"Skipping '{target_name}': Google Drive export size limit exceeded. "
                "Please export/download this file manually."
            )
            return
        raise

    # Save the file
    fh.seek(0)
    destination_path.parent.mkdir(parents=True, exist_ok=True)
    with destination_path.open("wb") as f:
        f.write(fh.read())
    print(f"Downloaded: {destination_path}")


def _is_export_size_limit_error(error: HttpError) -> bool:
    """Return True when Drive cannot export because the generated file is too large."""
    if getattr(error.resp, "status", None) != 403:
        return False

    try:
        payload = json.loads(error.content.decode("utf-8"))
    except (AttributeError, UnicodeDecodeError, json.JSONDecodeError):
        return False

    details = payload.get("error", {}).get("errors", [])
    return any(detail.get("reason") == "exportSizeLimitExceeded" for detail in details)

def list_files_in_folder(folder_id, service):
    """List all files in the specified folder, including created time."""
    results = service.files().list(
        q=f"'{folder_id}' in parents",
        fields="nextPageToken, files(id, name, mimeType, createdTime)"
    ).execute()
    files = results.get('files', [])
    print(f"Found {len(files)} files in folder ID {folder_id}.")
    return files

def format_creation_date(created_time):
    """Convert the created time to a formatted string for filenames."""
    dt = datetime.fromisoformat(created_time[:-1])  # Remove the 'Z' at the end
    return dt.strftime("%Y-%m-%d_%H-%M-%S")

def download_presentations_in_folder(folder_id, service, overwrite):
    """Download all presentations in the specified folder recursively and flatten the results."""
    files = list_files_in_folder(folder_id, service)
    for file in files:
        if file["name"].startswith("Copy of"):
            print(f"Skipping duplicate copy by name: {file['name']} (ID: {file['id']})")
            continue

        print(f"Processing file: {file['name']} (ID: {file['id']})")
        # Check if the file is a Google Slides presentation
        if file['mimeType'] == 'application/vnd.google-apps.presentation':
            # Create local file name (flattening the structure)
            sanitized_file_name = sanitize_file_name(file['name'])
            creation_date = format_creation_date(file['createdTime'])
            local_file_name = PRESENTATIONS_DIR / f"{sanitized_file_name}_{creation_date}.pdf"
            download_file(file['id'], local_file_name, service, file['mimeType'], overwrite)
        elif file['mimeType'] == 'application/vnd.google-apps.folder':
            # Recursively process the folder
            print(f"Found folder: {file['name']} (ID: {file['id']}). Descending into this folder.")
            download_presentations_in_folder(file['id'], service, overwrite)

def sanitize_file_name(file_name):
    """Sanitize the file name by replacing invalid characters."""
    return file_name.replace('/', '_').replace('\\', '_').replace(':', '_')

def get_folder_id(folder_name, service):
    """Get the ID of a folder by its name."""
    results = service.files().list(
        q=f"mimeType='application/vnd.google-apps.folder' and name='{folder_name}'",
        fields="files(id, name)"
    ).execute()
    items = results.get('files', [])
    if items:
        folder_id = items[0]['id']
        print(f"Found folder '{folder_name}' with ID: {folder_id}.")
        return folder_id
    else:
        print(f"Folder '{folder_name}' not found.")
        return None

def main(overwrite):
    """Main function to download presentations."""
    creds = None
    create_folder_if_not_exists(PRESENTATIONS_DIR)

    # Load credentials from the token file
    if TOKEN_PATH.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_PATH), SCOPES)
        print(f"Loaded credentials from {TOKEN_PATH.name}.")
    else:
        print("No valid token found, need to authorize the application.")

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Refreshed expired credentials.")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_PATH), SCOPES
            )
            creds = flow.run_local_server(
                port=0,
                open_browser=not args.noauth_local_webserver,
                noauth_local_webserver=args.noauth_local_webserver
            )
            print("Obtained new credentials.")

        with TOKEN_PATH.open("w") as token:
            token.write(creds.to_json())
            print(f"Saved credentials to {TOKEN_PATH.name}.")

    try:
        # Build the Google Drive service
        service = build("drive", "v3", credentials=creds)
        print("Google Drive service created.")

        # Get the ID of the 'UKY_Research' folder
        uky_research_id = get_folder_id('UKY_Research', service)
        if not uky_research_id:
            return
        
        # Get the ID of the 'Presentations' folder inside 'UKY_Research'
        presentations_id = get_folder_id('Presentations', service)

        # Get the ID of the 'Simulation Progress Reports' folder inside 'UKY_Research'
        simulation_reports_id = get_folder_id('Simulation Progress Reports', service)

        # Get the ID of the 'UKY Group Reports' folder inside 'UKY_Research'
        uky_group_reports_id = get_folder_id('UKY Group Reports', service)

        # Download all presentations from both folders if they exist
        if presentations_id:
            print("\nDownloading presentations from 'Presentations' folder...")
            download_presentations_in_folder(presentations_id, service, overwrite)

        if simulation_reports_id:
            print("\nDownloading presentations from 'Simulation Progress Reports' folder...")
            download_presentations_in_folder(simulation_reports_id, service, overwrite)
        
        if uky_group_reports_id:
            print("\nDownloading presentations from 'UKY Group Reports' folder...")
            download_presentations_in_folder(uky_group_reports_id, service, overwrite)


    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download presentations from Google Drive.')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files.')
    parser.add_argument('--noauth_local_webserver', action='store_true', help='Use manual authentication instead of a local web server.')
    args = parser.parse_args()

    main(args.overwrite)
