"""
Contains stuff related to yt_dlp package
"""
import yt_dlp


SEARCH_OPTS = {
    "format": "bestaudio/best",
    "quiet": True,  
    "default_search": "ytsearch",  
    "noplaylist": True,  
}

def get_download_options(dir_path, song, quality):
    """
    Returns the downloading options for a song with specified quality
    Parameters
    - dir_path  : server directory path
    - song      : song name - without quality and extension
    - quality   : song's quality bit rate (kbps)
    """
    download_options = {
        "format": "bestaudio/best",  
        "outtmpl": f"{dir_path}/{song} {quality} kbps.%(ext)s",  
        "quiet": True,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",  
                "preferredcodec": "mp3",  
                "preferredquality": quality,  
            },
            {
                "key": "FFmpegVideoConvertor",
                "preferedformat": "mp3",
            },
        ]
    }
    return download_options

def get_youtube_url(query):
    """
    Returns the first result's watch URL from youtube when searched using
    search_query(param) using yt_dlp
    """
    search_query = f"ytsearch:{query} audio"  
    print(f"Search query: {search_query}")

    try:
        with yt_dlp.YoutubeDL(SEARCH_OPTS) as ydl:
            result = ydl.extract_info(search_query, download=False)  
            if "entries" in result and result["entries"]:
                video = result["entries"][0]  
                print(video['title'], "-", video['webpage_url'])
    except:
        print(f'Cannot get url for {search_query} this search query')
    else:
        with yt_dlp.YoutubeDL(SEARCH_OPTS) as ydl:
            result = ydl.extract_info(search_query, download=False)  
            if "entries" in result and result["entries"]:
                video = result["entries"][0]  
                print(video['title'], "-", video['webpage_url'])
                return video["webpage_url"]

    return None
