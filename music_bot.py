"""
Discord bot to play music in a voice chat.
"""
import discord
import yt_dlp as dlp
import random as r
import asyncio
from discord.ext import commands
from pathlib import Path

CHANNEL_ID = 1183668996923465738

# Setting up intents for bot to receive events related to 
# server members and access content of messages.
intents = discord.Intents.default()
intents.members = True
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents) # Bot command prefix (currently commands are prefixed with a !)

playlist = Path(__file__).parent / 'playlist.txt' # Current file to store playlist songs
bot.song_stopped = False

dlp.utils.bug_reports_message = '' # Remove uneccessary clutter in console for readability


ytdl_format_options = {
    'format': 'bestaudio/best',  # Chooses the best audio quality (and video if available)
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',  # Template for output file names
    'restrictfilenames': True,  # Restricts filenames to only ASCII characters, and avoids "&" and spaces in filenames
    'noplaylist': True,  # Ensures that only a single video is downloaded, not a playlist
    'nocheckcertificate': True,  # Skips SSL certificate verification (use with caution)
    'ignoreerrors': False,  # Continues on download errors, skipping problematic videos
    'logtostderr': False,  # Logs to stderr instead of stdout
    'quiet': True,  # Activates quiet mode, reducing the output to the console
    'no_warnings': True,  # Suppresses warning messages
    'default_search': 'auto',  # Uses auto as the default search engine in youtube-dl
    'source_address': '0.0.0.0'  # Binds the socket to a specific source address (IPv4)
}

ffmpeg_options = {
    'options': '-vn', # Gets rid of video option, plays audio only
    "before_options": "-reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 5" # Allows song reconnect
}

ytdl = dlp.YoutubeDL(ytdl_format_options) # Initialize the YoutubeDL object with the specified format options.

class YTDLSource(discord.PCMVolumeTransformer):
    """
    A class that interfaces with the youtube-dl library to fetch and stream audio from various sources,
    mainly YouTube, and play it in a Discord voice channel.

    This class inherits from discord.PCMVolumeTransformer which allows for volume adjustments of
    the audio streams it manages.

    Attributes:
        data (dict): A dictionary containing metadata about the audio source.
        title (str): The title of the audio source.
        url (str): The direct URL to the audio source.

    Methods:
        __init__(source, *, data, volume=0.5): Initializes the YTDLSource instance.
        from_url(cls, url, *, loop=None, stream=False): Class method to create an instance of YTDLSource from a URL.
    """
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

# Command to make music bot join user's voice channel
@bot.command(name='join', help='Tells the bot to join the voice channel')
async def join(ctx):
    proceed = True  # Flag to determine if the main logic should proceed

    # Check if the command is used in the specified channel
    if ctx.channel.id != CHANNEL_ID:
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

# Gets the song title to be used to display in chat
def get_song_title(url):
    ydl_opts = {
        'quiet': True,
        'format': 'bestaudio',
    }

    with dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        song_title = info_dict.get('title', None)

    return song_title

# Command to add a song to the playlist
@bot.command(name='add_song', help="Add specified song (url) to playlist.")
async def add_song(ctx, *, url):
    async with ctx.typing():
        # Open the playlist file with the ability to read and append
        with open(playlist, 'a+') as file:
            file.seek(0)  # Move to the beginning to read
            content = file.read()
            # Only add the song if it does not exist in the playlist
            if url in content:
                await ctx.send("This song already exists in your playlist")
            else:
                file.write(url + '\n')  # Write URL on a new line
                await ctx.send(f'{get_song_title(url)} has been added to the playlist')

# Command to play a song from a specified YouTube URL.
@bot.command(name='play', help="Play a song by typing '!play (song url here)'")
async def play(ctx, *, url):
    # Force bot to join user's voice channel if not in already
    if not ctx.voice_client:
        await ctx.invoke(join)

    async with ctx.typing():
        player = await YTDLSource.from_url(url, loop=bot.loop, stream=True)
        bot.current_song = player.title
        ctx.voice_client.play(player, after=lambda e: print(f'Player error: {e}') if e else None)

    await ctx.send(f'Now playing: {player.title}')

# Command to shuffle the playlist 
@bot.command(name='shuffle', help='Play a random song from the playlist')  
async def shuffle(ctx):
    previous = None
    asyncio.run_coroutine_threadsafe(play_next_song(ctx, previous), ctx.bot.loop)

# Schedule the 'play_next_song' coroutine to run on the bot's asyncio event loop. 
# This is necessary because the current context is in a different thread 
def play_song_finished(error, ctx, previous):
    if error:
        print(f'An error has occurred: {error}')
    else:
        asyncio.run_coroutine_threadsafe(play_next_song(ctx, previous), ctx.bot.loop)

# Plays the next song as soon as the previous song has finished in the shuffle.
async def play_next_song(ctx, previous):
    try:
        url = None
        with open(playlist, 'r') as file:
            lines = file.readlines()

        if lines:
            url = r.choice(lines).strip()
            if len(lines) > 1:  # Check if there is more than one song
                while url == previous:
                    url = r.choice(lines).strip()

        if url and ctx.voice_client and ctx.voice_client.is_connected():
            player = await YTDLSource.from_url(url, loop=ctx.bot.loop, stream=True)
            bot.current_song = player.title
            await ctx.send(f'Now playing: {player.title}')
            
            after = lambda e: play_song_finished(e, ctx, url) if bot.song_stopped else None
            ctx.voice_client.play(player, after=after)
        else:
            print("No URL found or the bot is not connected to a voice channel.")
    except Exception as e:
        print(f"Error in play_next_song: {e}")

       

# Command to play the mmkay mp3 
@bot.command(name='mmkay', help='The almighty mmkay')
async def mmkay(ctx):
    # TODO: implement mmmkay voiceover function.
    return None


# Stops the current song from playing.
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

# Function to run the bot, used in main.py
def run_bot(token):
    bot.run(token)