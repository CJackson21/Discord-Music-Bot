import yt_dlp as dlp

def get_song_title(url):
    ydl_opts = {'quiet': True, 'format': 'bestaudio'}
    with dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=False)
        return info.get('title', 'Unknown Title')
