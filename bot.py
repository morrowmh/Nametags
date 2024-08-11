import discord
import os
import logging
import constants
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
from configtools import read_config, write_config

bot = discord.Bot(activity=discord.Game(name="/nametags help"))
logger = logging.getLogger(__name__)

# Main command group
nametags = discord.SlashCommandGroup("nametags")

# Help command
@nametags.command(name="help", description="Provides information about this bot")
async def help_(ctx: discord.ApplicationContext) -> None:
    await ctx.respond("TODO: implement help")

# Setup command
@nametags.command(name="setup", description="Initial bot setup")
@discord.option("nametags_channel_id", type=discord.SlashCommandOptionType.string, description="The channel ID where nametags are to be posted")
@discord.option("commands_channel_id", type=discord.SlashCommandOptionType.string, description="The channel ID where bot commands are to be performed (leave blank for global)")
async def setup(ctx: discord.ApplicationContext, nametags_channel_id: str, commands_channel_id: str | None=None) -> None:
    logger.info("Command: " + str(ctx.command) + " from user " + str(ctx.author) + " in guild " + str(ctx.author.guild.id))

    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Error: you must be an administrator to perform this command!")
        return
    
    commands_channel_id = -1 if commands_channel_id is None else commands_channel_id

    # Validate user input
    try:
        nametags_channel_id = int(nametags_channel_id)
    except Exception:
        await ctx.respond("Error: specified nametags_channel_id is invalid!")
        return
    
    try:
        commands_channel_id = int(commands_channel_id)
    except Exception:
        await ctx.respond("Error: specified commands_channel_id is invalid!")

    nametags_channel = ctx.author.guild.get_channel(nametags_channel_id)
    commands_channel = ctx.author.guild.get_channel(commands_channel_id)
    if nametags_channel is None:
        await ctx.respond("Error: specified nametags_channel_id is not a valid channel!")
        return
    
    if commands_channel_id != -1 and commands_channel is None:
        await ctx.respond("Error: specified commands_channel_id is not a valid channel!")
        return

    # Write config
    guild_config = {"nametags_channel_id": nametags_channel_id, "commands_channel_id": commands_channel_id}
    write_config("guilds/" + str(nametags_channel.guild.id) + "/config.toml", guild_config, logger=logger)

    # Reload guild config
    guild_configs[str(nametags_channel.guild.id)] = guild_config

    logger.info("Success: " + "guilds/" + str(nametags_channel.guild.id) + "/config.toml updated")
    
    await ctx.respond(f"Set nametags channel to {nametags_channel.name} and commands channel to {"GLOBAL" if commands_channel is None else commands_channel.name}")

@nametags.command(name="currentconfig", description="Check bot configuration")
async def status(ctx: discord.ApplicationContext) -> None:
    logger.info("Command: " + str(ctx.command) + " from user " + str(ctx.author) + " in guild " + str(ctx.author.guild.id))

    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Error: you must be an administrator to perform this command!")
        return
    
    guild = str(ctx.author.guild.id)
    await ctx.respond("nametags_channel_id=" + str(guild_configs[guild]["nametags_channel_id"]) + " AND commands_channel_id=" + str(guild_configs[guild]["commands_channel_id"]))

@nametags.command(name="reloadconfig", description="Reload bot configuration")
async def reloadconfig(ctx: discord.ApplicationContext) -> None:
    logger.info("Command: " + str(ctx.command) + " from user " + str(ctx.author) + " in guild " + str(ctx.author.guild.id))

    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Error: you must be an administrator to perform this command!")
        return
    
    guild_configs[str(ctx.guild.id)] = read_config("guilds/" + str(ctx.guild.id) + "/config.toml", constants.DEFAULT_GUILD_CONFIG)

    await ctx.respond("Success!")

@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
        # Ensure guild directory exists
        os.makedirs("guilds/" + str(guild.id), exist_ok=True)

        guild_configs[str(guild.id)] = read_config("guilds/" + str(guild.id) + "/config.toml", constants.DEFAULT_GUILD_CONFIG)

        logger.info("Joined guild " + str(guild.id))

@bot.event
async def on_ready() -> None:
    global guild_configs
    guild_configs = {}

    # Ensure guilds directory exists
    os.makedirs("guilds", exist_ok=True)

    # Load guild configs
    for guild in bot.guilds:
        # Ensure guild directory exists
        os.makedirs("guilds/" + str(guild.id), exist_ok=True)

        guild_configs[str(guild.id)] = read_config("guilds/" + str(guild.id) + "/config.toml", constants.DEFAULT_GUILD_CONFIG)
    
    logger.info(f"Ready! Logged in as {bot.user}")

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

    global bot_config
    bot_config = read_config("config.toml", constants.DEFAULT_BOT_CONFIG)

    setup_logging()

    # Add command group
    bot.add_application_command(nametags)

    print("\nStarting", bot_config["bot"]["name"], "v" + bot_config["bot"]["version"])
    load_dotenv()
    bot.run(os.getenv("TOKEN"))

if __name__ == "__main__":
    main()