"""
Contains methods related to database operations
"""
from webpage.models import VideoLog
from datetime import datetime, timedelta


# File (audio/directory) expiring duration in minutes
# EXPIRES_IN = 5  * 60
EXPIRES_IN = 15


def check_db(song_name, quality, f_type='YT', spotify_id=None):
    """Checks database for file and returns False if file exists"""
    qureysets = get_queryset(f_type)

    db_check = True
    
    for data in qureysets:
        print(data.file_name)
        print(data.file_audio_quality)
        if (song_name and 
            song_name == data.file_name and
            data.file_audio_quality == quality):
            db_check = False

        if (spotify_id and
            get_spotify_id(data) == spotify_id and
            data.file_audio_quality == quality):
            db_check = False

    print(f'Check db result {db_check}')
    return db_check

def get_spotify_id(file):
    """Returns spotify id from the end of file metadata"""
    return file.file_metadata.split('__')[-1]

def get_queryset(f_type):
    """Returns content from db by file type(f_type:param)"""
    if f_type == 'YT':
        return VideoLog.object.filter(file_metadata__startswith='yt')
    return VideoLog.object.filter(file_metadata__startswith='sp')

def get_existing_file(song_name, f_id, quality):
    """returns qurey with attrs from param"""
    if f_id.startswith('yt_'):
        return VideoLog.object.filter(
            file_audio_quality=quality
        ).filter(file_name=song_name).first()
    else:
        return VideoLog.object.filter(
            file_metadata__endswith=f_id.split("__")[-1]
        ).filter(file_audio_quality=quality).first()


def get_file_expiration_time():
    """
    Returns the expiration time from now calculated by EXPIRES_IN (global var)
    """
    expiration_time =  datetime.now().replace(tzinfo=None) + timedelta(minutes=EXPIRES_IN)
    return expiration_time

def log_file(filename, filepath, metadata, filetype, quality):
    """Logs new file to database"""
    batch_id = 1010
    new_file = VideoLog(
        file_path=filepath,
        file_type=filetype,
        file_metadata=metadata,
        expires_at=get_file_expiration_time(),
        batch_id=batch_id,
        file_audio_quality=quality
    )
    if filename:
        new_file.file_name = filename
    print('file saved to db:', new_file.__dict__)
    new_file.save()
