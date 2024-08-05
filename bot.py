import discord
import toml
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from configdict import configdict
from dotenv import load_dotenv

bot = discord.Bot()
logger = logging.getLogger(__name__)

# Constants
NAMETAGES_BOT_TITLE = "Nametags Discord Bot v1.0.0"
DEFAULT_CONFIG = {
    "logging": {
        "base_level": "INFO",
        "file": "logs/bot.log",
        "rotate_daily": True,
        "backup_count": 50,
        "disable_file_logging": False,
        "disable_console_logging": False
    }
}

@bot.event
async def on_ready():
    print(f"Ready! Logged in as {bot.user}")

def initialize():
    print("Reading configuration file")
    try:
        config_file = open("config.toml", "r")
    except FileNotFoundError:
        print("config.toml not found, falling back to defaults")
        config = DEFAULT_CONFIG
    else:
        with config_file:
            config = toml.load(config_file)

            # Handle missing keys
            config = configdict(DEFAULT_CONFIG)
    
    # Configure logging
    logger.setLevel(str(config["logging"]["base_level"]))
    formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    
    if not config["logging"]["disable_file_logging"]:
        # Ensure directory exists
        log_file = str(config["logging"]["file"])
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        print("Enabling file logging with " + log_file)

        file_handler = TimedRotatingFileHandler(log_file, backupCount=config["logging"]["backup_count"], when="midnight", interval=1)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    if not config["logging"]["disable_console_logging"]:
        print("Enabling console logging")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

def main():
    print(NAMETAGES_BOT_TITLE)
    print("\nInitializing...")
    initialize()

    print("\nStarting bot...")
    load_dotenv()
    bot.run(os.getenv("TOKEN"))

if __name__ == "__main__":
    main()