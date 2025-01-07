# Discord Music Bot

A feature-rich Discord bot for playing music from YouTube and Spotify.

## Features

- Play songs from YouTube or Spotify.
- Queue and shuffle songs.
- Spotify playlist integration.

## Setup

### Prerequisites

- Python 3.8+
- FFmpeg installed on your system.
- Spotify Developer App credentials.

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/your-repo/discord-music-bot.git
   cd discord-music-bot
   ```

2. Install dependencies:

```
pip install -r requirements.txt
```

3. Configure .env

```
DISCORD_BOT_TOKEN=your_discord_token
CHANNEL_ID=your_channel_id
SPOTIFY_PLAYLIST_ID=your_spotify_playlist_id
```

### Running the Bot

Start the bot:

```
python main.py
```

### Commands

- !join: summons the bot to your voice channel
- !play <[query]>: Play a song from YouTube
- !queue [query]: Queue a song
- !spotify_play: Play songs from Spotify playlist
- !stop: Stop playback
- !leave: Disconnect from the voice channel

### License

MIT Licence

- This structure improves maintainability and separates concerns for better scalability. Let me know if you’d like additional tweaks!
