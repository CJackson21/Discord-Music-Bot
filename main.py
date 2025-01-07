from music_bot import run_bot
from dotenv import load_dotenv
import os

# Load environment variables from the .env file
load_dotenv()

# Retrieve the Discord bot token from the loaded environment variables
bot_token = os.getenv('DISCORD_BOT_TOKEN')

def main():
    """
    Entry point of the application.
    Ensures the bot starts using the provided Discord bot token.
    """
    if not bot_token:
        # If the token is missing, log an error and exit the program
        raise ValueError("DISCORD_BOT_TOKEN is not set in the environment variables.")
    
    # Start the bot
    run_bot(bot_token)

# If the script is executed directly (not imported), run the main function
if __name__ == "__main__":
    main()
