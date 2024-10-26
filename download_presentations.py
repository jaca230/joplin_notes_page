import os
import io
import argparse
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload
from datetime import datetime

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def create_folder_if_not_exists(folder_name):
    """Create a folder if it doesn't already exist."""
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
        print(f"Created folder: {folder_name}")

def download_file(file_id, file_name, service, mime_type, overwrite):
    """Download a file from Google Drive."""
    if os.path.exists(file_name) and not overwrite:
        print(f"File already exists and overwrite is set to False: {file_name}. Skipping download.")
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
    print(f"Starting download: {file_name}")
    while done is False:
        status, done = downloader.next_chunk()
        print(f"Download {int(status.progress() * 100)}% complete for {file_name}.")

    # Save the file
    fh.seek(0)
    with open(file_name, "wb") as f:
        f.write(fh.read())
    print(f"Downloaded: {file_name}")

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
        print(f"Processing file: {file['name']} (ID: {file['id']})")
        # Check if the file is a Google Slides presentation
        if file['mimeType'] == 'application/vnd.google-apps.presentation':
            # Create local file name (flattening the structure)
            sanitized_file_name = sanitize_file_name(file['name'])
            creation_date = format_creation_date(file['createdTime'])
            local_file_name = os.path.join('Presentations', f"{sanitized_file_name}_{creation_date}.pdf")  # Change extension to .pdf
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

    # Load credentials from the token file
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
        print("Loaded credentials from token.json.")
    else:
        print("No valid token found, need to authorize the application.")

    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
            print("Refreshed expired credentials.")
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
            print("Obtained new credentials.")

        with open("token.json", "w") as token:
            token.write(creds.to_json())
            print("Saved credentials to token.json.")

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
        if not presentations_id:
            return

        # Download all presentations from the 'Presentations' folder
        download_presentations_in_folder(presentations_id, service, overwrite)

    except HttpError as error:
        print(f"An error occurred: {error}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Download presentations from Google Drive.')
    parser.add_argument('--overwrite', action='store_true', help='Overwrite existing files.')
    args = parser.parse_args()

    main(args.overwrite)
