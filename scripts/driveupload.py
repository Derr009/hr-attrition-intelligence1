from __future__ import print_function
import os.path
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import pickle

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate():
    creds = None
    # Load credentials if they exist
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If no valid creds, do OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    return creds

def upload_file(file_path, folder_id=None):
    creds = authenticate()
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {'name': os.path.basename(file_path)}
    if folder_id:
        file_metadata['parents'] = [folder_id]  # optional: upload to specific folder

    media = MediaFileUpload(file_path, mimetype='text/csv')
    file = service.files().create(body=file_metadata,
                                  media_body=media,
                                  fields='id').execute()
    print(f"File uploaded: {file.get('id')}")

# Usage
upload_file('merged_dataset.csv', folder_id='1BCUppWFKusRa1pAmcWsV6cJqtKm9LpyX')

 # Replace with your CSV path
# upload_file('your_file.csv', folder_id='your_google_drive_folder_id')  # If you want to put it inside a folder
