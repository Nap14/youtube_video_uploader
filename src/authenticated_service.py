import os
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from google.auth.exceptions import RefreshError

class Oauth2Service:
    SCOPES = ['https://www.googleapis.com/auth/youtube']

    def __init__(self, logging):
        self.logging = logging

    def autorize(self, secrets_file: str):
        self.logging.info("Asking user to authorize via browser...")
        flow = InstalledAppFlow.from_client_secrets_file(
            secrets_file, self.SCOPES)
    
        return flow.run_local_server(port=0)

    def get_youtube_service(self, token_file: str, secrets_file: str):
        """Authorize in YouTube API."""
        credentials = None
        
        if os.path.exists(token_file):
            try:
                credentials = Credentials.from_authorized_user_file(token_file, self.SCOPES)
            except Exception as e:
                self.logging.warning(f"Failed to load token file: {e}. Re-authorizing...")
        
        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                try:
                    self.logging.info("Refreshing access token...")
                    credentials.refresh(Request())
                except RefreshError as e:
                    self.logging.warning(f"Refresh token expired or invalid: {e}. Re-authorizing...")
                    credentials = self.autorize(secrets_file)
                except Exception as e:
                    self.logging.error(f"Unexpected error during token refresh: {e}. Re-authorizing...")
                    credentials = self.autorize(secrets_file)
            else:
                credentials = self.autorize(secrets_file)
            
            with open(token_file, 'w') as token:
                token.write(credentials.to_json())

        return build('youtube', 'v3', credentials=credentials)