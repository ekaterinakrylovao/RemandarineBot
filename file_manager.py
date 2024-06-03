import os

FILE_DIR = 'files'

if not os.path.exists(FILE_DIR):
    os.makedirs(FILE_DIR)

def save_file(file_id, file_content):
    file_path = os.path.join(FILE_DIR, file_id)
    with open(file_path, 'wb') as f:
        f.write(file_content)
    return file_path

def get_file_path(file_id):
    return os.path.join(FILE_DIR, file_id)

def delete_file(file_id):
    file_path = get_file_path(file_id)
    if os.path.exists(file_path):
        os.remove(file_path)
