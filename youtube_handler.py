import yt_dlp as dlp

ytdl_format_options = {
    'format': 'bestaudio/best',
    'noplaylist': True,
    'quiet': True,
}
ytdl = dlp.YoutubeDL(ytdl_format_options)

class YTDLSource:
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        return data['url'] if stream else ytdl.prepare_filename(data)

async def search_youtube(query):
    try:
        info = ytdl.extract_info(f"ytsearch:{query}", download=False)
        return info['entries'][0]['webpage_url'] if info['entries'] else None
    except Exception:
        return None
