from music_bot import run_bot
from dotenv import load_dotenv
import os

load_dotenv()
bot_token = os.getenv('DISCORD_BOT_TOKEN')

def main():
    run_bot(bot_token)

if __name__ == "__main__":
    main()
