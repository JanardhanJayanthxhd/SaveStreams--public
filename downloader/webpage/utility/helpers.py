from webpage.models import KeyLog

from datetime import datetime, timedelta

from . import get_file_type
from .spotify import get_token
from .ytdlp import get_youtube_url, get_download_options
from .file import get_song_filename, get_download_dir
from .db import log_file, check_db, get_existing_file
import time
import yt_dlp



def calculate_duration(length) -> str:
    """
    Returns duration(as string)
    ...
    Parameter :
    - length(int) : length of the Youtube video in seconds.
    """
    audio_length = length
    nearest_mul = audio_length // 60
    remaining_secs = audio_length - (nearest_mul * 60)

    if remaining_secs < 10:
        remaining_secs = '0' + str(remaining_secs)
    duration = f'{nearest_mul}:{remaining_secs}'

    return duration

def download_songs(
        song_list: list[str], collection_id: str, filename: str, filepath: str, quality: int, playlist: bool
    ):
    """
    Downloads spotify playlist/album to server and logs file info to db
    Parameters:
    - song_list     : list containing all track names from listing in webpage
    - collection_id : spotify playlist/album id
    - filename      : unique directory name
    - filepath      : filepath to that directory in server
    - quality       : song quality - bitrate (kpbs)
    - playlist      : boolean flag to set metadata
    """
    for song in song_list:
        yt_url = get_youtube_url(song)
        if yt_url:
            download(song, filepath, quality, yt_url)
        else:
            print(f'Cannot download {song}')

    log_file(
        filepath=filepath,
        filetype='directory',
        metadata=get_metadata(collection_id, playlist),
        filename=filename,
        quality=quality
    )

def download_song(song_name, file_meta, quality, yt_url):
    """
    Downloads track
    Parameters:
    - song_name: Track name without bit rate or extension
    - filepath : directory path to track
    - file_meta  : file metadata
    """
    filepath = get_download_dir()
    full_song_name = get_song_filename(song_name, quality)

    if file_meta == 'yt_audio':
        db_check_status = check_db(
            song_name=full_song_name, quality=quality
        )
    else:
        db_check_status = check_db(
            song_name='', quality=quality, f_type='SP', spotify_id=file_meta.split('__')[-1]
        )

    if db_check_status:
        download(song_name, filepath, quality, yt_url)
        log_file(
            filename=full_song_name,
            filepath=filepath,
            metadata=file_meta,
            filetype=get_file_type(file_meta),
            quality=quality
        )
        return full_song_name, filepath
    else:
        existing_file = get_existing_file(song_name=full_song_name, f_id=file_meta, quality=quality)
        return existing_file.file_name, existing_file.file_path

def download(song_name, filepath, quality, yt_url):
    """Downloads a song using yt_dlp package"""
    download_opts = get_download_options(
        dir_path=filepath, song=song_name, quality=quality
    )
    with yt_dlp.YoutubeDL(download_opts) as ydl:
        print(f'{song_name} Downloaded on server')
        ydl.download(yt_url)

def get_metadata(collection_id: str, is_playlist: bool) -> str:
    """Returns file metadata for playlist/album"""
    meta_string = f'sp_album__{collection_id}'
    if is_playlist:
        meta_string = f'sp_playlist__{collection_id}'
    return meta_string

def get_spotify_token(add_new=False):
    """
    Checks KeyLog table if api_key already exists:
    if it exists then returns it, else return new (got from Spotify API) one.
    ...
    Parameter :
    - add_new : used only when called by scheduler
    """
    existing_tokens = KeyLog.object.all()
    print(f'Existing token list {existing_tokens}')
    
    if len(existing_tokens) == 0:
        result = get_new_spotify_token()
    else:
        recent_token = existing_tokens.last()
        if check_expiration(recent_token.expires_at):
            result = get_new_spotify_token()
        else:
            result = recent_token.api_token

    if not add_new:
        print(f'returnd a sp token {result}')
        return result
    return None


def check_expiration(expiration_time: datetime.time) -> bool:
    """Checks expiration time for existing(most recent) spotify token"""
    current_time = datetime.now()
    print(f'Current time: {current_time}')
    print(f'Received time: {expiration_time}')
    if expiration_time < current_time:
        return True
    return False

def get_new_spotify_token() -> str:
    """Returns a new spotify token"""
    token = get_token()
    time.sleep(1)
    save_token(token)
    return token

def save_token(token):
    """Saves spotify token to database"""
    new_token = KeyLog(
        api_token=token,
        expires_at=datetime.now().replace(tzinfo=None) + timedelta(seconds=3600)
    )
    new_token.save()






