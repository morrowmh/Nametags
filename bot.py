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
    bot_config = read_config("config.toml", constants.DEFAULT_BOT_CONFIG)

    global guild_configs
    guild_configs = {}

    # Ensure guilds directory exists
    os.makedirs("guilds", exist_ok=True)

    # Load each guild config
    for guild_dir in os.listdir("guilds"):
        guild_configs[guild_dir] = read_config("guilds/" + guild_dir + "/config.toml", constants.DEFAULT_GUILD_CONFIG)

def setup_logging() -> None:
    logger.setLevel(bot_config["logging"]["base_level"])
    formatter = logging.Formatter("%(asctime)s :: %(levelname)s :: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")
    
    if not bot_config["logging"]["disable_file_logging"]:
        # Ensure logs directory exists
        os.makedirs("logs", exist_ok=True)

        print("Enabling file logging")

        # Daily logfile rotation
        file_handler = TimedRotatingFileHandler("logs/bot.log", backupCount=bot_config["logging"]["logfile_backup_count"], when="midnight", interval=1)
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