import sqlite3
import discord

def open_table(ctx: discord.ApplicationContext) -> tuple[sqlite3.Cursor, sqlite3.Connection]:
    con = sqlite3.connect("guilds/" + str(ctx.guild.id) + "/data.db")
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS nametags(userid INTEGER PRIMARY KEY, title TEXT, body TEXT)")
    con.commit()
    return cur, con

def nametag_exists(ctx: discord.ApplicationContext, cur: sqlite3.Cursor) -> bool:
    res = cur.execute("SELECT userid FROM nametags WHERE userid=?", (ctx.author.id,))
    return res.fetchone() is not None