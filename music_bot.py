import discord
import youtube_dl
from discord.ext import commands
import yt_dlp as youtube_dl
import random as r
import asyncio
from dotenv import load_dotenv
import os



channel_id = 1183668996923465738
load_dotenv()
bot_token = os.getenv('DISCORD_BOT_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.message_content = True

# Bot command prefix
bot = commands.Bot(command_prefix='!', intents=intents)
bot.previous = []
playlist = 'playlist.txt'
bot.song_stopped = False

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''

ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # IPv4
}

ffmpeg_options = {
    'options': '-vn',
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5"
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.5):
        super().__init__(source, volume)

        self.data = data
        self.title = data.get('title')
        self.url = data.get('url')

    @classmethod
    async def from_url(cls, url, *, loop=None, stream=False):
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # Take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(discord.FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    proceed = True  # Flag to determine if the main logic should proceed

    # Check if the command is used in the specified channel
    if ctx.channel.id != channel_id:
        await ctx.send("This command cannot be used in this channel.")
        proceed = False

    # Check if the user is in a voice channel
    elif not ctx.message.author.voice:
        await ctx.send("You are not connected to a voice channel")
        proceed = False

    # Main logic for joining the voice channel
    if proceed:
        channel = ctx.message.author.voice.channel

        if ctx.voice_client is not None:
            await ctx.voice_client.move_to(channel)
        else:
            await channel.connect()

def get_song_title(url):
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio',
    }

    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        song_title = info_dict.get('title', None)

    return song_title

@bot.command(name='add_song', help="Add specified song (url) to playlist.")
async def add_song(ctx, *, url):
    async with ctx.typing():
        with open(playlist, 'a+') as file:
            file.seek(0)  # Move to the beginning to read
            content = file.read()
            if url in content:
                await ctx.send("This song already exists in your playlist")
            else:
                file.write(url + '\n')  # Write URL on a new line
                await ctx.send(f'{get_song_title(url)} has been added to the playlist')

@bot.command(name='play', help="Play a song by typing '!play (song url here)'")
async def play(ctx, *, url):
    if not ctx.voice_client:
        await ctx.invoke(join)

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        bot.current_song = player.title
        ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

    await ctx.send(f'Now playing: {player.title}')

@bot.command(name='shuffle', help='Play a random song from the playlist')  
async def shuffle(ctx):
    previous = None
    asyncio.run_coroutine_threadsafe(play_next_song(ctx, previous), ctx.bot.loop)

def play_song_finished(error, ctx, previous):
    if error:
        print(f'An error has occurred: {error}')
    else:
        asyncio.run_coroutine_threadsafe(play_next_song(ctx, previous), ctx.bot.loop)

async def play_next_song(ctx, previous):
    url = None
    with open(playlist, 'r') as file:
        lines = file.readlines()

    if lines:
        url = r.choice(lines).strip()
        while url == previous:
            url = r.choice(lines).strip()

    if url:
        after = None
        if bot.song_stopped:
            after = lambda e :play_song_finished(e, ctx, url)
        else:
            after = lambda e: print(f'Player error: {e}') if e else None
        player = await YTDLSource.from_url(url, loop=ctx.bot.loop, stream=True)
        bot.current_song = player.title
        await ctx.send(f'Now playing: {player.title}')
        
        ctx.voice_client.play(player, after=after)
       

@bot.command(name='mmkay', help='The almighty mmkay')
async def mmkay(ctx):
    # TODO: implement mmmkay voiceover function.
    return None


@bot.command(name='stop', help="Stop the current song")
async def stop(ctx):
    voice_client = ctx.voice_client
    if voice_client and voice_client.is_playing():
        voice_client.stop()
        await ctx.send(f'Stopped playing {bot.current_song}')
        bot.song_stopped = True
        del bot.current_song


@bot.command(name='leave', help='To leave voice channel')
async def leave(ctx):
    await ctx.voice_client.disconnect()

bot.run(bot_token)
