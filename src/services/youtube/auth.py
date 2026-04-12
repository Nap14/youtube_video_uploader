import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

class Oauth2Service:
    SCOPES = ['https://www.googleapis.com/auth/youtube']
    
    def __init__(self, logger):
        self.logger = logger

    def authorize_new(self, secrets_file):
        self.logger.info("New browser authorization...")
        flow = InstalledAppFlow.from_client_secrets_file(secrets_file, self.SCOPES)
        return flow.run_local_server(port=0)

    def get_service(self, token_path, secrets_path):
        creds = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
            
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except:
                    creds = self.authorize_new(secrets_path)
            else:
                creds = self.authorize_new(secrets_path)
            
            with open(token_path, 'w') as f:
                f.write(creds.to_json())

        return build('youtube', 'v3', credentials=creds)
