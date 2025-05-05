"""
Contains methods related to file operations
"""
import os
import io
import uuid
import zipfile
from datetime import datetime

from django.conf import settings


def get_zip_buffer(filename: str, filepath: str) -> io.BytesIO:
    """
    Returns zip buffer after using it to write downloaded playlist/album songs from server to
    the zip file for download
    parameters:
    - filename: Unique directory name
    - filepath: Path to that directory
    """
    zip_buffer = io.BytesIO()

    with zipfile.ZipFile(zip_buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        for root, _, files in os.walk(filepath):
            for file in files:
                file_path = os.path.join(root, file)
                zip_file.write(file_path, os.path.relpath(file_path, filename))

    zip_buffer.seek(0)

    return zip_buffer


def get_filename(path):
    """
    Returns the directory name at the end of the file path.
    """
    normalized_path = os.path.normpath(str(path))
    file_name = os.path.basename(normalized_path)
    print(f'File name {file_name}, datatype {type(file_name)}')
    return file_name

def fix_filename(filename):
    """
    Fixes filename by replacing invalid symbols with empty string('')
    Returns valid filename
    """
    symbols = ['.', '/', '\\', '|', '*', '>', '<', '"', ':', '?']

    if filename:
        for symbol in symbols:
            filename = filename.replace(symbol, '')

    return filename

def get_unique_directory_path():
    """
    Returns the absolute path of a unique directory inside 
    files(server download) directory
    """
    unique_dir_name = f'{uuid.uuid4().hex[:8]}_{datetime.now().strftime("%Y%m%d%H%M%S")}'
    base_dir = os.path.join(settings.BASE_DIR, '..\\files')
    return os.path.join(base_dir, unique_dir_name)

def get_download_dir():
    """Returns the server folder location for downloading tracks"""
    download_dir = os.path.join(settings.BASE_DIR, "..\\files") 
    os.makedirs(download_dir, exist_ok=True)
    print('server download location: ', download_dir)
    return download_dir

def get_song_filename(song_name, quality):
    """Returns full song name with its quality(bit rate) and extension"""
    return f'{song_name} {quality} kbps.mp3'

def get_file_type(f_id):
    """Return file type for saving to a database"""
    contents = f_id.split('_')
    if contents[1] in ['audio', 'track']:
        return 'audio'
    return 'directory'

