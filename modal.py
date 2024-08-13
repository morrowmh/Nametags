import discord
import sqltools
import embed
from logging import Logger

class ChannelNotFoundException(Exception):
    ...

class NametagModal(discord.ui.Modal):
    def __init__(self, ctx: discord.ApplicationContext, guild_config: dict, bot_config: dict, logger: Logger, *args, is_update: bool=False, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ctx = ctx
        self.guild_config = guild_config
        self.bot_config = bot_config
        self.is_update = is_update
        self.logger = logger

        channel = self.ctx.author.guild.get_channel(self.guild_config["nametags_channel_id"])
        if channel is None:
            raise ChannelNotFoundException("Error: nametags channel not found! Have an admin use `/nametags setup`")
        self.channel = channel

        # Get prefills if update
        if self.is_update:
            cur, con = sqltools.open_table(ctx)
            prefill_name, prefill_age, prefill_location, prefill_bio = sqltools.grab_nametag_data(ctx.author, cur)
            con.close()
        else:
            prefill_name = prefill_age = prefill_location = prefill_bio = ""

        self.add_item(discord.ui.InputText(label="Name", value=prefill_name))
        self.add_item(discord.ui.InputText(label="Age", value=prefill_age, required=guild_config["require_age"]))
        self.add_item(discord.ui.InputText(label="Location", value=prefill_location, required=guild_config["require_location"]))
        self.add_item(discord.ui.InputText(label="Bio", value=prefill_bio, style=discord.InputTextStyle.long))

    async def callback(self, interaction: discord.Interaction) -> None:
        cur, con = sqltools.open_table(self.ctx)

        if self.is_update:
            # Write to database
            cur.execute("UPDATE nametags SET name=?, age=?, location=?, bio=? WHERE userid=?", (
                *[self.children[i].value for i in range(4)],
                self.ctx.author.id
            ))
            con.commit()

            # Attempt to delete old message
            await sqltools.delete_old_message(self.ctx, cur, self.channel, self.logger)
        else:
            # Write to database
            cur.execute("INSERT INTO nametags(userid, name, age, location, bio) VALUES(?,?,?,?,?)", (
                self.ctx.author.id,
                *[self.children[i].value for i in range(4)]
            ))
            con.commit()
        
        em = embed.nametag_embed(self.ctx.bot, self.ctx.author, cur, self.bot_config["bot"]["name"] + " v" + self.bot_config["bot"]["version"])
        send = await self.channel.send("", embed=em)

        # Update msgid
        cur.execute("UPDATE nametags SET msgid=? WHERE userid=?", (send.id, self.ctx.author.id))
        con.commit()

        con.close()
        await interaction.response.send_message("Success!")
        self.logger.info("Success!")