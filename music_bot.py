import asyncio
import discord
from discord.ext import commands, tasks
import logging
import os
from pathlib import Path
from spotify_handler import SpotifyHandler
from utils import get_song_title
from youtube_handler import YTDLSource, search_youtube


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Intents and bot setup
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# Bot settings
CHANNEL_ID = int(os.getenv('CHANNEL_ID', 0))
playlist_path = Path(__file__).parent / 'playlist.txt'
bot.spotify_handler = SpotifyHandler()
bot.song_queue = []
bot.current_song = None

@bot.event
async def on_ready():
    logger.info(f"{bot.user.name} has connected to Discord!")
    bot.spotify_handler.start_task()

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
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

@bot.command(name='play', help="Play a song from a query")
async def play(ctx, *, query):
    url = await search_youtube(query)
    if not ctx.voice_client:
        await ctx.invoke(join)
    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        bot.current_song = player.title
        ctx.voice_client.play(player)
    await ctx.send(f"Now playing: {player.title}")

@bot.command(name='queue', help="Queue a song")
async def queue(ctx, *, query):
    url = await search_youtube(query)
    bot.song_queue.append(url)
    await ctx.send(f"Added {get_song_title(url)} to the queue")

@bot.command(name='spotify_play', help="Play songs from Spotify playlist")
async def spotify_play(ctx):
    bot.spotify_handler.play_from_spotify(ctx)

@bot.command(name='stop', help="Stop the current song")
async def stop(ctx):
    if ctx.voice_client.is_playing():
        ctx.voice_client.stop()
        await ctx.send("Playback stopped.")

@bot.command(name='leave', help="Disconnect the bot from the voice channel")
async def leave(ctx):
    if ctx.voice_client:
        await ctx.voice_client.disconnect()

def run_bot(token):
    bot.run(token)
