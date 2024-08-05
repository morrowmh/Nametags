import discord
import toml
import logging
from logging.handlers import TimedRotatingFileHandler
from collections import defaultdict
from os import getenv
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
async def on_ready() -> None:
    print(f"Ready! Logged in as {bot.user}")

def initialize() -> None:
    print("Reading configuration file")
    try:
        config_file = open("config.toml", "r")
    except FileNotFoundError:
        print("config.toml not found, falling back to defaults")
        config = DEFAULT_CONFIG
    else:
        with config_file:
            config = toml.load(config_file)
    
    # Configure logging
    logger.setLevel(config["logging"]["base_level"])
    formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    
    if not config["logging"]["disable_file_logging"]:
        print("Enabling file logging with " + config["logging"]["file"])
        file_handler = TimedRotatingFileHandler(config["logging"]["file"], backupCount=config["logging"]["backup_count"], when="midnight", interval=1)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    if not config["logging"]["disable_console_logging"]:
        print("Enabling console logging")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

def main() -> None:
    print(NAMETAGES_BOT_TITLE)
    print("Initializing...")
    initialize()

    print("Starting bot...")
    load_dotenv()
    bot.run(getenv("TOKEN"))

if __name__ == "__main__":
    main()