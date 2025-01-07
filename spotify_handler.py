import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from youtube_handler import search_youtube

class SpotifyHandler:
    """
    A handler class for managing Spotify playlist integration with the bot.

    This class retrieves tracks from a Spotify playlist, converts them to YouTube URLs, 
    and facilitates playback in the Discord bot.
    """
    def __init__(self):
        """
        Starts the process of updating the Spotify playlist periodically.
        This method is called during bot startup to ensure the playlist is kept up-to-date.
        """
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope='playlist-read-private'))
        self.spotify_playlist = {}

    def start_task(self):
        """
        Starts the process of updating the Spotify playlist periodically.
        This method is called during bot startup to ensure the playlist is kept up-to-date.
        """
        self.update_spotify_playlist()

    def update_spotify_playlist(self):
        """
        Updates the Spotify playlist by fetching the tracks and converting them to YouTube URLs.

        - Retrieves tracks from the Spotify playlist specified by `SPOTIFY_PLAYLIST_ID`.
        - For each track, constructs a search query combining the track name and artist.
        - Uses the `search_youtube` function to find a YouTube URL for each track.
        - Stores the mapping of Spotify track IDs to YouTube URLs in `self.spotify_playlist`.
        """
        playlist_id = os.getenv('SPOTIFY_PLAYLIST_ID')
        tracks = self.sp.playlist_tracks(playlist_id)['items']
        for item in tracks:
            track = item['track']
            query = f"{track['name']} {track['artists'][0]['name']}"
            url = search_youtube(query)
            self.spotify_playlist[track['id']] = url

    async def play_from_spotify(self, ctx):
        """
        Plays songs from the Spotify playlist in the Discord voice channel.

        - Iterates over the stored YouTube URLs in `self.spotify_playlist`.
        - Uses the bot's play command to queue and play each song.
        """
        for _, url in self.spotify_playlist.items():
            await ctx.invoke(ctx.bot.get_command('play'), query=url)
