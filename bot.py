import discord
import os
import constants
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
from configtools import read_config

bot = discord.Bot()
logger = logging.getLogger(__name__)

@bot.event
async def on_ready() -> None:
    logger.info(f"Ready! Logged in as {bot.user}")

def load_configs() -> None:
    global bot_config
    bot_config = read_config(constants.DEFAULT_BOT_CONFIG_FILENAME, constants.DEFAULT_BOT_CONFIG)

def setup_logging() -> None:
    logger.setLevel(bot_config["logging"]["base_level"])
    formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    
    if not bot_config["logging"]["disable_file_logging"]:
        # Ensure directory exists
        log_file = bot_config["logging"]["file"]
        os.makedirs(os.path.dirname(log_file), exist_ok=True)

        print("Enabling file logging with " + log_file)

        # Daily logfile rotation
        file_handler = TimedRotatingFileHandler(log_file, backupCount=bot_config["logging"]["backup_count"], when="midnight", interval=1)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    if not bot_config["logging"]["disable_console_logging"]:
        print("Enabling console logging")
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

def main() -> None:
    print("Initializing")

    load_configs()
    setup_logging()

    print("\nStarting", bot_config["bot"]["name"], "v" + bot_config["bot"]["version"])
    load_dotenv()
    bot.run(os.getenv("TOKEN"))

if __name__ == "__main__":
    main()