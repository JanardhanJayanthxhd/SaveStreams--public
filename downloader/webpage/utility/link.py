import re
from urllib.parse import urlparse, ParseResult

NETLOC = {
    'spotify': ['open.spotify.com'],
    'youtube': ['www.youtube.com', 'youtu.be']
}

RE_PLAYLIST = r'/playlist/'
RE_TRACK = r'/track/'
RE_ALBUM = r'/album/'


def detect_link_type(link: str) -> str:
    """Detects """
    parsed_url = parse_link(link)
    if parsed_url.netloc in NETLOC['youtube']:
        return 'youtube'
    elif parsed_url.netloc in NETLOC['spotify']:
        return detect_spotify_link_type(parsed_url.path)
    else:
        return 'Invalid'

def parse_link(link: str) -> ParseResult:
    """Returns prase result of an input link"""
    return urlparse(link)

def detect_spotify_link_type(path: str) -> str:
    """detects spotify playlist/album/track link using regular expression"""
    if re.match(RE_PLAYLIST, path):
        return 'spotify playlist'
    elif re.match(RE_TRACK, path):
        return 'spotify track'
    elif re.match(RE_ALBUM, path):
        return 'spotify album'
    return 'Invalid'
