from urllib.parse import urlparse
import yt_dlp
import os

from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import FileResponse, HttpResponse
from .models import VideoLog

from webpage.utility import (
    fix_filename, get_unique_directory_path, check_db,  SEARCH_OPTS, detect_link_type, parse_link,
    calculate_duration, download_song, download_songs, get_filename, get_spotify_token, get_zip_buffer,
    get_playlist_tracks, get_playlist_info, get_album_info, get_track_info, get_album_tracks, get_youtube_url,
)


"""
check yt and sp trock routs for downloading, caching (save & delete)
"""

def home(request):
    """Home page"""
    # Delete all logs
    # VideoLog.object.all().delete()

    if request.method == 'POST':
        input_link = request.POST['link']

        request.session['link'] = input_link
        request.session['parsed_link'] = parse_link(input_link)

        redirect_to = detect_link_type(input_link)
        if redirect_to != 'Invalid':
            return redirect(redirect_to)
        else:
            messages.info(request, 'Invalid Link! Use a valid Youtube or Spotify share link')
            return redirect('home')

    return render(request, 'webpage/index.html')

def youtube(request):
    """Youtube audio page"""
    link = request.session.get('link', '')

    try:
        with yt_dlp.YoutubeDL(SEARCH_OPTS) as ydl:
            link_info = ydl.extract_info(link, download=False)
    except Exception as e:
        print(f'Error: {e}')
        messages.info(request, 'Unable to download this song')
        return redirect('home')

    if request.method == 'POST':
        filename_input = request.POST['filename_input']
        youtubelink_input = request.POST['youtubelink_input']
        quality_option = request.POST['inlineRadioOptions']

        filename = fix_filename(filename_input)

        file_to_download, filepath = download_song(
            song_name=filename,
            yt_url=youtubelink_input,
            quality=quality_option,
            file_meta='yt_audio'
        )

        response = FileResponse(open(os.path.join(filepath, file_to_download), 'rb'),
                                as_attachment=True, filename=file_to_download)

        return response

    return render(request, 'webpage/youtube.html', {
        'title': link_info["title"],
        'thumbnail': link_info["thumbnail"],
        'yt_link' : link_info["webpage_url"],
        'duration': calculate_duration(link_info["duration"])
    })

def spotify_playlist(request):
    """Spotify playlist page"""
    link = request.session.get('link', '')
    playlist_id = request.session.get('parsed_link')[2].split('/')[-1]
    token = get_spotify_token()
    playlist_songs = get_playlist_tracks(token, playlist_id)

    if playlist_songs:
        songs_len = len(playlist_songs)
        print(playlist_songs)

        if request.method == "POST":
            # print('downloading playlist - posted')
            song_quality = request.POST["inlineRadioOptions"]
            dir_path = get_unique_directory_path()
            file_name = get_filename(dir_path)

            if check_db(file_name, song_quality, 'SP', playlist_id):
                song_list = []
                for i in range(1, songs_len + 1):
                    if request.POST.get(f'song_check_{i}') is not None:
                        song = request.POST.get(f'song_name_{i}')
                        if song is not None:
                            song_list.append(fix_filename(song))

                download_songs(
                    song_list=song_list, collection_id=playlist_id, filename=file_name, filepath=dir_path,
                    quality=song_quality, playlist=True
                )
            else:
                existing_dir = VideoLog.object.get(
                    file_metadata__endswith=playlist_id
                )
                dir_path = existing_dir.file_path
                file_name = get_filename(dir_path)

            response = HttpResponse(get_zip_buffer(filename=file_name, filepath=dir_path), 'application/zip')
            response['Content-Disposition'] = f'attachment; filename={file_name}.zip'

            return response

        return render(request, 'webpage/spotify playlist.html',{
            'link': link, 'link_type': 'spotify',
            'songs': playlist_songs, 'song_len': songs_len,
            'info': get_playlist_info(token, playlist_id),
        })
    else:
        messages.error(request, 'Error. Try again')
        return redirect('home')

def spotify_album(request):
    """Spotify album page"""
    link = request.session.get('link', '')
    album_id = request.session.get('parsed_link')[2].split('/')[-1]
    token = get_spotify_token()
    album_songs = get_album_tracks(token, album_id)

    if album_songs:
        songs_len = len(album_songs)

        if request.method == "POST":
            # print('downloading album')
            song_quality = request.POST["inlineRadioOptions"]
            dir_path = get_unique_directory_path()
            file_name = get_filename(dir_path)

            if check_db(file_name, song_quality, 'SP', album_id):
                song_inputs = []
                for i in range(1, songs_len + 1):
                    if request.POST.get(f'song_check_{i}') is not None:
                        song = request.POST.get(f'song_name_{i}')
                        if song is not None:
                            song_inputs.append(fix_filename(song))

                download_songs(
                    song_list=song_inputs, collection_id=album_id, filename=file_name, filepath=dir_path,
                    quality=song_quality, playlist=False
                )

            else:
                existing_dir = VideoLog.object.get(
                    file_metadata__endswith=album_id
                )
                dir_path = existing_dir.file_path
                file_name = get_filename(dir_path)

            response = HttpResponse(get_zip_buffer(filename=file_name, filepath=dir_path), 'application/zip')
            response['Content-Disposition'] = f'attachment; filename={file_name}.zip'

            return response

        return render(request, 'webpage/spotify album.html',{
            'link': link, 'link_type': 'spotify',
            'songs': album_songs, 'song_len': songs_len,
            'info': get_album_info(token, album_id)
        })
    else:
        messages.info(request, 'Error Try again')
        return redirect('home')

def spotify_track(request):
    """Spotify track page"""
    # From Spotify playlist listing page
    api_link = request.GET.get('api_link')

    # From home page
    link = request.session.get('link', '')
    token = get_spotify_token()

    if api_link:# got from listing
        track_id = urlparse(api_link).path.split('/')[-1]
    else:# got from home page
        parsed_link = urlparse(link)
        track_id = parsed_link.path.split('/')[-1]

    if request.method == "POST":
        file_name = fix_filename(request.POST.get('filenameinput'))
        quality_option = request.POST['inlineRadioOptions']

        song_to_download, filepath = download_song(
            song_name=file_name,
            yt_url=get_youtube_url(file_name),
            quality=quality_option,
            file_meta=f'sp_track__{track_id}'
        )

        response = FileResponse(open(os.path.join(filepath, song_to_download), 'rb'),
                                as_attachment=True, filename=song_to_download)

        return response
    return render(request, 'webpage/spotify track.html',{
        'track': get_track_info(token=token, track_id=track_id)
    })

def info_page(request):
    """'How to ?' page"""
    return render(request, 'webpage/info.html')
