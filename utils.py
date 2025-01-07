import yt_dlp as dlp

def get_song_title(url):
    """
    Retrieves the title of a song or video from a given URL.

    Args:
        url (str): The URL of the media to fetch the title from.

    Returns:
        str: The title of the media, or 'Unknown Title' if the title cannot be determined.
    """
    ydl_opts = {'quiet': True, 'format': 'bestaudio'}
    with dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('title', 'Unknown Title')
