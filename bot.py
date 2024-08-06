import discord
import os
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
from configtools import read_config

bot = discord.Bot()
logger = logging.getLogger(__name__)
config = {}

# Constants
NAMETAGS_BOT_TITLE = "Nametags Discord Bot v1.0.0"
NAMETAGS_CONFIG_FILE = "config.toml"
NAMETAGS_DEFAULT_CONFIG = {
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
    logger.info(f"Ready! Logged in as {bot.user}")

def initialize():
    config = read_config(NAMETAGS_CONFIG_FILE, NAMETAGS_DEFAULT_CONFIG)

    # Configure logging
    logger.setLevel(config["logging"]["base_level"])
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
    print(NAMETAGS_BOT_TITLE)
    print("\nInitializing...")
    initialize()

    print("\nStarting bot...")
    load_dotenv()
    bot.run(os.getenv("TOKEN"))

if __name__ == "__main__":
    main()