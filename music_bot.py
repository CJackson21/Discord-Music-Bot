import asyncio
import discord
from discord.ext import commands, tasks
import logging
import os
from pathlib import Path
from spotify_handler import SpotifyHandler
from utils import get_song_title
from youtube_handler import YTDLSource, search_youtube

# Initialize Discord intents for bot functionality
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intents and bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Load bot settings from environment variables
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))
playlist_path = Path(__file__).parent / 'playlist.txt'
bot.spotify_handler = SpotifyHandler()
bot.song_queue = []
bot.current_song = None

# Event: Triggered when the bot successfully connects to Discord
@bot.event
async def on_ready():
    """
    This event runs when the bot is ready and connected to Discord.
    Initializes the Spotify playlist update task.
    """
    logger.info(f"{bot.user.name} has connected to Discord!")
    bot.spotify_handler.start_task()

# Command: Makes the bot join the voice channel of the user who invoked the command@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    """
    Joins the voice channel of the command author.
    Restricts the command to a specific text channel and ensures the user is in a voice channel.
    """
    if ctx.channel.id != CHANNEL_ID:
        await ctx.send("This command cannot be used in this channel.")
        return
    if not ctx.author.voice:
        await ctx.send("You are not connected to a voice channel.")
        return
    channel = ctx.author.voice.channel
    if ctx.voice_client:
        await ctx.voice_client.move_to(channel)
    else:
        await channel.connect()

# Command: Plays a song based on a search query or YouTube URL
@bot.command(name='play', help="Play a song from a query")
async def play(ctx, *, query):
    """
    Plays a song in the user's voice channel.
    Automatically joins the user's voice channel if not already connected.
    """
    url = await search_youtube(query)
    if not ctx.voice_client:
        await ctx.invoke(join)
    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        bot.current_song = player.title
        ctx.voice_client.play(player)
    await ctx.send(f"Now playing: {player.title}")

# Command: Queues a song for playback
@bot.command(name='queue', help="Queue a song")
async def queue(ctx, *, query):
    """
    Adds a song to the playback queue.
    Uses the search query to fetch the song URL and appends it to the queue.
    """
    url = await search_youtube(query)
    bot.song_queue.append(url)
    await ctx.send(f"Added {get_song_title(url)} to the queue")

# Command: Plays songs from a Spotify playlist
@bot.command(name='spotify_play', help="Play songs from Spotify playlist")
async def spotify_play(ctx):
    """
    Plays songs from a Spotify playlist.
    Delegates playback management to the SpotifyHandler class.
    """
    bot.spotify_handler.play_from_spotify(ctx)

# Command: Stops the currently playing song
@bot.command(name='stop', help="Stop the current song")
async def stop(ctx):
    """
    Stops the currently playing song.
    Does not clear the playback queue or disconnect the bot.
    """
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Playback stopped.")

# Command: Makes the bot leave the voice channel
@bot.command(name='leave', help="Disconnect the bot from the voice channel")
async def leave(ctx):
    """
    Disconnects the bot from the voice channel it is currently in.
    """
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

def run_bot(token):
    """
    Starts the bot using the provided Discord bot token.
    """
    bot.run(token)
