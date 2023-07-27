import os
from flask import Flask, request, jsonify
from collections import defaultdict
from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

#Add JSON credentials path 
credentials_path = 'client_secret_1006015286349-687cg6gerpmmtj6ipl6u12sdjpfur1vi.apps.googleusercontent.com.json'

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = credentials_path

#scopes for Google Drive API
SCOPES = ['https://www.googleapis.com/auth/drive']

app = Flask(__name__)

#Dictionaries to store in key value pairs
my_dict = {}

my_files = {}

def authenticate():
    creds = None

    # If refresh token exists, load it, otherwise start the authentication flow
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If no valid credentials are available, let the user log in and authorize the application
    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
        creds = flow.run_local_server(port=0)

        # Save the credentials for future use (including refresh token)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return creds

@app.route('/api/postdata', methods=['POST'])
def post_data():
    creds = authenticate()
    drive_service = build('drive', 'v3', credentials=creds)

    #Get files to interact with the Google Drive API.
    results = drive_service.files().list(pageSize=10, fields="nextPageToken, files(id, name)").execute()
    items = results.get('files', [])

    # Get the json request
    request_files = request.json

    # Fetch PDF files
    pdf_files = fetch_files_with_format(drive_service, 'application/pdf')
    add_file(drive_service,pdf_files)
         
    # Fetch Image files
    image_files = fetch_files_with_format(drive_service, 'image/jpeg')
    add_file(drive_service,image_files)
        
    # Fetch ZIP files
    zip_files = fetch_files_with_format(drive_service, 'application/zip')
    add_file(drive_service,zip_files)

     # Fetch XML files
    xml_files = fetch_files_with_format(drive_service, 'application/xml')
    add_file(drive_service,xml_files)

    # list the text files in your Drive:
    plain_files = fetch_files_with_format(drive_service, 'text/plain')
    add_file(drive_service,plain_files)

    # list the docs files in your Drive:
    add_file(drive_service,items)

    #Fetching the Files URL based on request
    for file_data in request_files['name']:    
        data_file = my_dict[file_data]   
        my_files[file_data] = data_file

    response_data = {'message': 'Fetched the data Successfully from Google Drive', 'received_data': my_files}

    return jsonify(response_data)      

def add_file(drive_service,files):
    for file_iterate in files:
         # Fetch the URL of the file
        url = get_file_link(drive_service,file_iterate['id'])
        my_dict[file_iterate['name']] = url        

def get_file_link(drive_service,file_id):
   url = drive_service.files().get(fileId=file_id, fields="webViewLink").execute()
   return url.get("webViewLink")            

def fetch_files_with_format(drive_service, mime_type):
    # Fetch the files based on mime_type
    results = drive_service.files().list(q=f"mimeType='{mime_type}'", fields="files(id, name)").execute()
    items = results.get('files', [])
    return items    

if __name__ == '__main__':
    app.run(debug=True)
    
