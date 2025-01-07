import os
import spotipy
from spotipy.oauth2 import SpotifyOAuth
from youtube_handler import search_youtube

class SpotifyHandler:
    def __init__(self):
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope='playlist-read-private'))
        self.spotify_playlist = {}

    def start_task(self):
        # Fetch and update Spotify playlist periodically
        self.update_spotify_playlist()

    def update_spotify_playlist(self):
        playlist_id = os.getenv('SPOTIFY_PLAYLIST_ID')
        tracks = self.sp.playlist_tracks(playlist_id)['items']
        for item in tracks:
            track = item['track']
            query = f"{track['name']} {track['artists'][0]['name']}"
            url = search_youtube(query)
            self.spotify_playlist[track['id']] = url

    async def play_from_spotify(self, ctx):
        for track_id, url in self.spotify_playlist.items():
            await ctx.invoke(ctx.bot.get_command('play'), query=url)
