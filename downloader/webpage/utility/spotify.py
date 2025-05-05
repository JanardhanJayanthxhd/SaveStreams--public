import os
from requests import get, post
from json import loads
from base64 import b64encode
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

client_id = os.getenv('CLIENT_ID')
client_secret = os.getenv('CLIENT_SECRET')
# print(client_id, client_secret)

def get_token():
    """
    returns a spotify token
    (which expires in 1 hour)
    """
    auth_str = client_id + ':' + client_secret
    auth_byte = auth_str.encode('utf-8')
    auth_b64 = str(b64encode(auth_byte), 'utf-8')

    url = 'https://accounts.spotify.com/api/token'
    headers = {
        'Authorization': 'Basic ' + auth_b64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    res = post(url, data=data, headers=headers)
    json_res = loads(res.content)
    token = json_res["access_token"]

    return token


def get_auth_header(token):
    """
    Returns the header dictionary for spotify API
    """
    return {'Authorization': 'Bearer ' + token}


def get_playlist_info(token, pl_id):
    """
    Returns a list with playlist info
    ...
    Parameter :
    - token   : Spotify api token
    - pl_id   : Spotify's playlist id
    Return Example
    [playlist_name, playlist_cover url, owner's display name, link_to_that profile]
    """
    url = f'https://api.spotify.com/v1/playlists/{pl_id}'
    header = get_auth_header(token)
    info = []

    res = get(url=url, headers=header)
    if res.status_code == 200:
        json_res = res.json()
        info.append(json_res['name']) # playlist name
        info.append(json_res['images'][0]['url']) # Playlist cover link
        info.append(json_res['owner']['display_name']) # owner's display name
        info.append(json_res['owner']['external_urls']['spotify']) # profile link

    return info


def get_track_info(token, track_api=None, track_id=None):
    """
    NOTE : Pass anyone parameter either track_api or track_id - By default it uses track_api link
    ...
    Parameter :
    - token     : Spotify API token
    - track_api : A Spotify track's api link
    - track_id  : A Spotify track's id
    Returns the info of a track using track_api_endpoint or track_id(param) and token(param)
    Example : [track_name, cover_url, artists, spotify_url, track_id]
    """
    if track_id is not None:
        url = f'https://api.spotify.com/v1/tracks/{track_id}'
    else:
        url = track_api

    header = get_auth_header(token)
    response = get(url=url, headers=header)

    result = {}
    if response.status_code == 200:
        res_json = response.json()
        result['name'] = res_json['name']  # Track name
        result['cover_url'] = res_json['album']['images'][0]['url'] # Album cover url
        artists = ''
        for artist in  res_json['artists']:
            if artists:
                artists += ', ' + artist['name']  # artists
            else:
                artists += artist['name']  # artists
        result['artists'] = artists
        result['spotify_link'] = res_json['external_urls']['spotify'] # spotify url
        result['track_id'] = urlparse(result['spotify_link']).path.split('/')[-1]
    else:
        result = None

    return result


def get_playlist_tracks(token, pl_id):
    """
    Uses token and pl_id(spotify playlist's id) from params
    to get info of a playlist using Spotify API.
    ...
    Parameters :
    - token    : Spotify API token
    - pl_id    : Spotify playlist's id
    Returns a list containing tuples for each track:
     (song_index(int), song_name(str), artists(str), track_api_link)
    """
    url = f'https://api.spotify.com/v1/playlists/{pl_id}'
    header = get_auth_header(token)
    song_artist = []
    count = 0

    while url:
        # print(url)
        res = get(url=url, headers=header)
        if res.status_code == 200:
            json_res = res.json()
            # If the playlist contains more than 100 tracks response is multipage
            try:
                json_res['tracks']['items']
            except KeyError:
                items = json_res['items']
            else:
                items = json_res['tracks']['items']

            for idx, i in enumerate(items, start=count + 1):
                song_name = i['track']['name']
                track_api_link = i['track']['href']
                artists = ''
                for artist in i['track']['artists']:
                    if artists:
                        artists += ', ' + artist['name']
                    else:
                        artists += artist['name']

                song_artist.append((idx, song_name, artists, track_api_link))
                count = idx

            # Exception handling to get the next link
            # because Spotify API only gives 100 tracks at once, if the playlist has more than 100 tracks.
            try:
                json_res['tracks']['next']
            except KeyError:
                url = json_res['next']
            else:
                url = json_res['tracks']['next']
        else:
            print(res.status_code)
            break

    return song_artist


def get_album_info(token, album_id):
    """
    Returns the info of an album using spotify_token(param) and album_id(param)
    info : [album_name, cover_url, artists, spotify_url]
    """
    result = []
    url = f'https://api.spotify.com/v1/albums/{album_id}'
    header = get_auth_header(token)
    response = get(url=url, headers=header)
    if response.status_code == 200:
        res_json = response.json()
        result.append(res_json["name"])
        result.append(res_json["images"][0]["url"])
        artists = ''
        for artist in res_json["artists"]:
            artists += artist["name"]
        result.append(artists)
        result.append(res_json["external_urls"]["spotify"])

    return result


def get_album_tracks(token, album_id):
    """
    Uses token and album_id(spotify album's id) from params
    to get info of an album using Spotify API.
    Returns a list containing tuples for each track:
    (song_index(int), song_name(str), artists(str), track_api_link)
    """
    url = f'https://api.spotify.com/v1/albums/{album_id}'
    header = get_auth_header(token)
    response = get(url=url, headers=header)
    tracks_info = []

    if response.status_code == 200:
        res_json = response.json()
        songs = res_json["tracks"]["items"]
        for i, song in enumerate(songs, start=1):
            song_name = song["name"]
            artists = ''
            for artist in song["artists"]:
                if artists:
                    artists += ', ' + artist["name"]
                else:
                    artists += artist["name"]
            track_api_link = song["href"]
            tracks_info.append((i, song_name, artists, track_api_link))

    return tracks_info
