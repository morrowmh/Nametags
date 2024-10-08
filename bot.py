import discord
import os
import sqltools
import logging
import constants
import embed
import modal
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv
from configtools import read_config, write_config

bot = discord.Bot(activity=discord.Game(name="/nametags help"))
logger = logging.getLogger(__name__)

# Main command group
nametags = discord.SlashCommandGroup("nametags")

# Channel validator
def validate_channels(ctx: discord.ApplicationContext, nametags_channel_id: str, commands_channel_id: str) -> tuple[discord.abc.GuildChannel, discord.abc.GuildChannel, int, int]:
    try:
        nametags_channel_id = int(nametags_channel_id)
    except Exception:
        raise Exception("Error: specified nametags_channel_id is not a valid integer!")
    
    try:
        commands_channel_id = int(commands_channel_id)
    except Exception:
        raise Exception("Error: specified commands_channel_id is not a valid integer!")
    
    nametags_channel = ctx.author.guild.get_channel(nametags_channel_id)
    commands_channel = ctx.author.guild.get_channel(commands_channel_id)
    if nametags_channel is None:
        raise Exception("Error: specified nametags_channel_id is not a valid channel!")
    
    if commands_channel_id != -1 and commands_channel is None:
        raise Exception("Error: specified commands_channel_id is not a valid channel!")
    
    return nametags_channel, commands_channel, nametags_channel_id, commands_channel_id

# Check command location
def is_in_commands_channel(ctx: discord.ApplicationContext) -> bool:
    guild_config = guild_configs[str(ctx.guild.id)]
    return True if guild_config["commands_channel_id"] == -1 or ctx.author.guild_permissions.administrator else ctx.channel.id == guild_config["commands_channel_id"]

# Help command
@nametags.command(name="help", description="Provides information about this bot")
async def help_(ctx: discord.ApplicationContext) -> None:
    logger.info("Command: " + str(ctx.command) + " from user " + str(ctx.author) + " in guild " + str(ctx.author.guild.id))
    if not is_in_commands_channel(ctx):
        await ctx.respond("Error: you are not in the correct commands channel!")
        return
    
    # Get bot avatar url
    av_url = bot.user.avatar.url

    # Make help embed
    help_embed = discord.Embed(title="Nametags Help", color=discord.Colour.magenta())
    help_embed.set_thumbnail(url=av_url)
    user_commands = """
                    `/nametags help` :: Display this message
                    `/nametags create` :: Create a new nametag
                    `/nametags update` :: Update an existing nametag
                    `/nametags view` :: View a user's nametag
                    `/nametags delete` :: Delete your nametag
                    """
    help_embed.add_field(name="User commands", value=user_commands, inline=False)
    admin_commands = """
                     `/nametags setup` :: Configure the bot
                     `/nametags showconfig` :: Display the current configuration
                     """
    help_embed.add_field(name="Admin commands", value=admin_commands, inline=False)
    
    await ctx.respond("", embed=help_embed)
    logger.info("Success!")

# Setup command
@nametags.command(name="setup", description="Bot configuration setup")
@discord.option("nametags_channel_id", type=discord.SlashCommandOptionType.string, description="The channel ID where nametags are to be posted")
@discord.option("commands_channel_id", type=discord.SlashCommandOptionType.string, description="The channel ID where bot commands are to be performed (default is global)")
@discord.option("require_age", type=discord.SlashCommandOptionType.boolean, description="Whether age is required in nametags (default is True)")
@discord.option("require_location", type=discord.SlashCommandOptionType.boolean, description="Whether location is required in nametags (default is True)")
async def setup(ctx: discord.ApplicationContext, nametags_channel_id: str, commands_channel_id: str="-1", require_age: bool=True, require_location: bool=True) -> None:
    logger.info("Command: " + str(ctx.command) + " from user " + str(ctx.author) + " in guild " + str(ctx.author.guild.id))

    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Error: you must be an administrator to perform this command!")
        return
    
    try:
        *_, nametags_channel_id, commands_channel_id = validate_channels(ctx, nametags_channel_id, commands_channel_id)
    except Exception as e:
        await ctx.respond(str(e))
        return

    # Write config
    guild_config = {"nametags_channel_id": nametags_channel_id, "commands_channel_id": commands_channel_id, "require_age": require_age, "require_location": require_location}
    write_config("guilds/" + str(ctx.guild.id) + "/config.toml", guild_config, logger=logger)
    guild_configs[str(ctx.guild.id)] = guild_config

    logger.info("Success: " + "guilds/" + str(ctx.guild.id) + "/config.toml updated")
    await ctx.respond("Configuration successfully updated!")

@nametags.command(name="showconfig", description="Check bot configuration")
async def showconfig(ctx: discord.ApplicationContext) -> None:
    logger.info("Command: " + str(ctx.command) + " from user " + str(ctx.author) + " in guild " + str(ctx.author.guild.id))

    if not ctx.author.guild_permissions.administrator:
        await ctx.respond("Error: you must be an administrator to perform this command!")
        return
    
    await ctx.respond(guild_configs[str(ctx.author.guild.id)])

# Create command
@nametags.command(name="create", description="Create a new nametag")
async def create(ctx: discord.ApplicationContext) -> None:
    logger.info("Command: " + str(ctx.command) + " from user " + str(ctx.author) + " in guild " + str(ctx.author.guild.id))

    if not is_in_commands_channel(ctx):
        await ctx.respond("Error: you are not in the correct commands channel!")
        return

    # Check if nametag already exists
    cur, con = sqltools.open_table(ctx)
    if sqltools.nametag_exists(ctx.author, cur):
        await ctx.respond("Error: you already have a nametag! Delete it with `/nametags delete` or update it with `/nametags update`")
        con.close()
        return
    con.close()

    try:
        mod = modal.NametagModal(ctx, guild_configs[str(ctx.guild.id)], bot_config, logger, title="Introduce yourself!")
    except modal.ChannelNotFoundException as e:
        await ctx.respond(str(e))
        return
    except Exception:
        await ctx.respond("Fatal error, check with an admin")
        logger.exception("")
        return
    
    await ctx.send_modal(mod)
    logger.info("Modal sent!")

# Delete command
@nametags.command(name="delete", description="Delete your nametag")
async def delete(ctx: discord.ApplicationContext) -> None:
    logger.info("Command: " + str(ctx.command) + " from user " + str(ctx.author) + " in guild " + str(ctx.author.guild.id))

    # Check if nametag exists
    cur, con = sqltools.open_table(ctx)
    if not sqltools.nametag_exists(ctx.author, cur):
        await ctx.respond("Error: you don't have a nametag! Try `/nametags create`")
        con.close()
        return
    
    # Attempt to delete old message
    channel = ctx.author.guild.get_channel(guild_configs[str(ctx.guild.id)]["nametags_channel_id"])
    await sqltools.delete_old_message(ctx, cur, channel, logger)

    # Delete nametag
    sqltools.delete_nametag(ctx, cur, con)
    con.close()

    await ctx.respond("Done!")
    logger.info("Success!")

# Update command
@nametags.command(name="update", description="Update your nametag")
async def update(ctx: discord.ApplicationContext) -> None:
    logger.info("Command: " + str(ctx.command) + " from user " + str(ctx.author) + " in guild " + str(ctx.author.guild.id))

    if not is_in_commands_channel(ctx):
        await ctx.respond("Error: you are not in the correct commands channel!")
        return

    # Check if nametag already exists
    cur, con = sqltools.open_table(ctx)
    if not sqltools.nametag_exists(ctx.author, cur):
        await ctx.respond("Error: you don't have a nametag! Try `/nametags create`")
        con.close()
        return
    con.close()

    try:
        mod = modal.NametagModal(ctx, guild_configs[str(ctx.guild.id)], bot_config, logger, is_update=True, title="Introduce yourself!")
    except modal.ChannelNotFoundException as e:
        await ctx.respond(str(e))
        return
    except Exception:
        await ctx.respond("Fatal error, check with an admin")
        logger.exception("")
        return

    await ctx.send_modal(mod)
    logger.info("Modal sent!")

# View command
@nametags.command(name="view", description="View a nametag")
@discord.option("user", type=discord.SlashCommandOptionType.user, description="User whose nametag should be viewed (default is self)")
async def view(ctx: discord.ApplicationContext, user: discord.User | discord.Member=None) -> None:
    logger.info("Command: " + str(ctx.command) + " from user " + str(ctx.author) + " in guild " + str(ctx.author.guild.id))

    if not is_in_commands_channel(ctx):
        await ctx.respond("Error: you are not in the correct commands channel!")
        return

    user = ctx.author if user is None else user

    # Check if nametag exists
    cur, con = sqltools.open_table(ctx)
    if not sqltools.nametag_exists(user, cur):
        await ctx.respond("Error: you don't have a nametag! Try `/nametags create`") if user == ctx.author else await ctx.respond(f"Error: user {user.name} doesn't have a nametag!")
        con.close()
        return

    await ctx.respond("", embed = embed.nametag_embed(bot, user, cur, bot_config["bot"]["name"] + " v" + bot_config["bot"]["version"]))
    con.close()
    logger.info("Success!")
    
@bot.event
async def on_guild_join(guild: discord.Guild) -> None:
        # Ensure guild directory exists
        os.makedirs("guilds/" + str(guild.id), exist_ok=True)

        # Write default config
        write_config("guilds/" + str(guild.id) + "/config.toml", constants.DEFAULT_GUILD_CONFIG, logger=logger)
        guild_configs[str(guild.id)] = constants.DEFAULT_GUILD_CONFIG

        logger.info("Joined guild " + str(guild.id))

@bot.event
async def on_ready() -> None:
    global guild_configs
    guild_configs = {}

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