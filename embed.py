import discord
import sqlite3
import sqltools

def nametag_embed(bot: discord.Bot, user: discord.User | discord.Member, cur: sqlite3.Cursor, bot_title: str) -> discord.Embed:
    # Get nametag data
    name, age, location, bio = sqltools.grab_nametag_data(user, cur)

    # Get avatar url
    av_url = user.avatar.url

    # Get bot avatar url
    bot_url = bot.user.avatar.url

    # Make embed
    ret = discord.Embed(title=user.name, color=discord.Colour.magenta())
    ret.add_field(name="Name", value=name, inline=False)
    ret.add_field(name="Age", value=age, inline=False)
    ret.add_field(name="Location", value=location, inline=False)
    ret.add_field(name="Bio", value=bio, inline=False)
    ret.set_thumbnail(url=av_url)
    ret.set_footer(text=f"Created with {bot_title}", icon_url=bot_url)

    return ret