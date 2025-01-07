import yt_dlp as dlp

ytdl_format_options = {
    'format': 'bestaudio/best',  # Fetch the best available audio quality
    'noplaylist': True,  # Ensure only a single video is processed, not an entire playlist
    'quiet': True,  # Suppress most output for cleaner logs
}

# Initialize a yt-dlp object with the defined options
ytdl = dlp.YoutubeDL(ytdl_format_options)

class YTDLSource:
    """
    A helper class for extracting and streaming audio from YouTube or similar platforms using yt-dlp.

    This class provides a method to fetch audio file URLs or download files for playback in a Discord bot.
    """
    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        """
        Fetches media information from a given URL and prepares it for streaming or downloading.

        Args:
            url (str): The URL of the media to fetch.
            loop (asyncio.AbstractEventLoop, optional): The event loop to use for asynchronous execution.
            stream (bool, optional): If True, fetches the direct URL for streaming without downloading.

        Returns:
            str: The direct URL to the media (for streaming) or the local file path (for downloaded files).
        """
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))
        return data['url'] if stream else ytdl.prepare_filename(data)

async def search_youtube(query):
    """
    Searches YouTube for a video matching the given query and returns the URL of the top result.

    Args:
        query (str): The search term to look for on YouTube.

    Returns:
        str or None: The URL of the top search result, or None if no results were found.
    """
    try:
        info = ytdl.extract_info(f"ytsearch:{query}", download=False)
        return info['entries'][0]['webpage_url'] if info['entries'] else None
    except Exception:
        return None
