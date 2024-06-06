from __future__ import print_function

import datetime
import os
import io
import subprocess
import zipfile
import base64
from google.auth.transport.requests import Request
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from dotenv import load_dotenv

# Загрузка переменных окружения из файла .env
load_dotenv()

# Настройки
SCOPES = ['https://www.googleapis.com/auth/drive']
SERVICE_ACCOUNT_FILE = 'service-account-file.json'
FOLDER_ID = os.getenv('FOLDER_ID')

# Аутентификация и создание сервиса
creds = Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('drive', 'v3', credentials=creds)


# Загрузка файлов из папки
def download_files(folder_id, download_path):
    query = f"'{folder_id}' in parents"
    results = service.files().list(q=query).execute()
    items = results.get('files', [])

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    for item in items:
        file_id = item['id']
        file_name = item['name']
        request = service.files().get_media(fileId=file_id)
        fh = io.FileIO(os.path.join(download_path, file_name), 'wb')
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while not done:
            status, done = downloader.next_chunk()
            print(f"Download {file_name} {int(status.progress() * 100)}%.")


# Архивирование и шифрование
def archive_and_encrypt(source_dir, output_file, password):
    with zipfile.ZipFile(output_file, 'w') as zipf:
        for root, dirs, files in os.walk(source_dir):
            for file in files:
                zipf.write(os.path.join(root, file),
                           os.path.relpath(os.path.join(root, file), source_dir))
    with open(output_file, 'rb') as f:
        data = f.read()
    encrypted_data = base64.b64encode(data)  # Пример простого шифрования
    with open(output_file + '.enc', 'wb') as f:
        f.write(encrypted_data)


def create_or_get_folder(parent_folder_id):
    now = datetime.datetime.now()
    folder_name = now.strftime("%Y-%m-%d")  # Текущая дата в формате YYYY-MM-DD

    # Проверяем, существует ли папка с текущей датой
    query = f"name='{folder_name}' and mimeType='application/vnd.google-apps.folder' and '{parent_folder_id}' in parents"
    results = service.files().list(q=query, fields='files(id)').execute()
    folders = results.get('files', [])

    # Если папка уже существует, берем ее id
    if folders:
        folder_id = folders[0]['id']
    else:
        # Если папка не существует, создаем ее
        file_metadata = {
            'name': folder_name,
            'parents': [parent_folder_id],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        folder_id = folder.get('id')

    return folder_id


# Загрузка архива обратно на Google Диск
def upload_file(file_path, parent_folder_id):
    folder_id = create_or_get_folder(parent_folder_id)
    file_metadata = {
        'name': os.path.basename(file_path),
        'parents': [folder_id]
    }
    media = MediaFileUpload(file_path, mimetype='application/zip')
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
    print(f'Uploaded file ID: {file.get("id")}')


def create_db_dump(db_dump_path, db_url, pg_dump_path):
    command = [
        pg_dump_path,  # Путь к pg_dump.exe
        '--dbname', db_url,
        '--file', db_dump_path
    ]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.returncode != 0:
        print("Ошибка при создании дампа базы данных:")
        print(result.stderr)
    else:
        print("Дамп базы данных успешно создан.")


# Основной поток
download_path = 'C:\\Users\\Katya\\Downloads\\jenkins_for\\download'
archive_path = 'C:\\Users\\Katya\\Downloads\\jenkins_for\\archive.zip'
db_dump_path = 'C:\\Users\\Katya\\Downloads\\jenkins_for\\db_dump.sql'

# Шаги выполнения
# 1. Скачивание файлов
download_files(FOLDER_ID, download_path)

# 2. Создание дампа базы данных
db_url = os.getenv('db_url')
# pg_dump_path = "C:\\Program Files\\PostgreSQL\\15\\bin\\pg_dump.exe"
pg_dump_path = "/usr/bin/pg_dump"
create_db_dump(db_dump_path, db_url, pg_dump_path)

# 3. Архивирование и шифрование
archive_and_encrypt(download_path, archive_path, 'yourpassword')
archive_and_encrypt(db_dump_path, db_dump_path + '.zip', 'yourpassword')

# 4. Загрузка архива обратно на Google Диск
upload_file(archive_path + '.enc', FOLDER_ID)
upload_file(db_dump_path + '.zip.enc', FOLDER_ID)
