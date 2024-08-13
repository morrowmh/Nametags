import sqlite3
import discord
from logging import Logger

def open_table(ctx: discord.ApplicationContext) -> tuple[sqlite3.Cursor, sqlite3.Connection]:
    con = sqlite3.connect("guilds/" + str(ctx.guild.id) + "/data.db")
    cur = con.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS nametags(
                userid INTEGER PRIMARY KEY,
                msgid INT UNIQUE,
                name TEXT NOT NULL,
                age TEXT,
                location TEXT,
                bio TEXT NOT NULL)""")
    con.commit()
    return cur, con

def nametag_exists(ctx: discord.ApplicationContext, cur: sqlite3.Cursor) -> bool:
    res = cur.execute("SELECT userid FROM nametags WHERE userid=?", (ctx.author.id,))
    return res.fetchone() is not None

def delete_nametag(ctx: discord.ApplicationContext, cur: sqlite3.Cursor, con: sqlite3.Connection) -> None:
    cur.execute("DELETE FROM nametags WHERE userid=?", (ctx.author.id,))
    con.commit()

async def delete_old_message(ctx: discord.ApplicationContext, cur: sqlite3.Cursor, logger: Logger) -> None:
    res = cur.execute("SELECT msgid FROM nametags WHERE userid=?", (ctx.author.id,))
    old_id = res.fetchone()
    try:
        msg = await ctx.channel.fetch_message(old_id[0])
        await msg.delete()
    except Exception:
        logger.info(f"Old message with ID {old_id[0]} not found, skipping deleting")