import os
from typing import Any, Protocol
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource

from src.core.logger import Logger

class Oauth2Service:
    SCOPES = ['https://www.googleapis.com/auth/youtube']
    
    def __init__(self, logger: Logger):
        self.logger = logger

    def authorize_new(self, secrets_file: str) -> Credentials:
        self.logger.info("New browser authorization...")
        flow = InstalledAppFlow.from_client_secrets_file(secrets_file, self.SCOPES)
        return flow.run_local_server(port=0)

    def get_service(self, token_path: str, secrets_path: str) -> Resource:
        creds: Any = None
        if os.path.exists(token_path):
            creds = Credentials.from_authorized_user_file(token_path, self.SCOPES)
        if not creds or not creds.valid:
            self._update_creds(creds, token_path, secrets_path)
        return build('youtube', 'v3', credentials=creds)

    def _update_creds(self, creds, token_path, secrets_path):
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except:
                creds = self.authorize_new(secrets_path)
        else:
            creds = self.authorize_new(secrets_path)

        self._save_creds(creds, token_path)
    
    def _save_creds(self, creds, token_path):
        with open(token_path, 'w', encoding='utf-8') as f:
            f.write(creds.to_json())
