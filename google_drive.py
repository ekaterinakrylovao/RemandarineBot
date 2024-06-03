# from __future__ import print_function
# import os.path
# from google.oauth2.credentials import Credentials
# from google.auth.transport.requests import Request
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload
#
# SCOPES = ['https://www.googleapis.com/auth/drive.file']
# SERVICE_ACCOUNT_FILE = 'path_to_your_service_account.json'
#
# creds = service_account.Credentials.from_service_account_file(
#     SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#
#
# def upload_file(file_path, file_name):
#     service = build('drive', 'v3', credentials=creds)
#     file_metadata = {'name': file_name}
#     media = MediaFileUpload(file_path, resumable=True)
#     file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
#     return file.get('id')


import os
import json
import google.auth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

# Файл с учетными данными (credentials.json), который вы получили в Google Cloud Console
CLIENT_SECRET_FILE = 'credentials.json'
SCOPES = ['https://www.googleapis.com/auth/drive']


def get_credentials():
    creds = None
    token_file = 'token.json'

    # Загружаем сохраненные токены, если они существуют
    if os.path.exists(token_file):
        creds = Credentials.from_authorized_user_file(token_file, SCOPES)

    # Если токены нет или он истек, получаем новые
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except google.auth.exceptions.RefreshError:
                print("The refresh token is invalid or expired, need to reauthenticate.")
                creds = None
        if not creds:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)

        # Сохраняем обновленные токены
        with open(token_file, 'w') as token:
            token.write(creds.to_json())

    return creds


# Пример использования
credentials = get_credentials()
