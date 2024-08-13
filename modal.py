import discord
import sqltools
from logging import Logger

class NametagModal(discord.ui.Modal):
    def __init__(self, ctx: discord.ApplicationContext, guild_config: dict, logger: Logger, *args, is_update: bool=False, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.ctx = ctx
        self.guild_config = guild_config
        self.is_update = is_update
        self.logger = logger

        # Get prefills if update
        if self.is_update:
            cur, con = sqltools.open_table(ctx)
            cur.execute("SELECT name, age, location, bio FROM nametags WHERE userid=?", (ctx.author.id,))
            prefill_name, prefill_age, prefill_location, prefill_bio = cur.fetchone()
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
            await sqltools.delete_old_message(self.ctx, cur, self.logger)
        else:
            # Write to database
            cur.execute("INSERT INTO nametags(userid, name, age, location, bio) VALUES(?,?,?,?,?)", (
                self.ctx.author.id,
                *[self.children[i].value for i in range(4)]
            ))
            con.commit()

        await interaction.response.send_message(f"Data: {self.children[0].value}, {self.children[1].value}, {self.children[2].value}, {self.children[3].value}")
        send = await interaction.original_response()

        # Update msgid
        cur.execute("UPDATE nametags SET msgid=? WHERE userid=?", (send.id, self.ctx.author.id))
        con.commit()

        con.close()
        self.logger.info("Success!")