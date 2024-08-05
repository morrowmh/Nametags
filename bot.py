import discord
import os
from dotenv import load_dotenv

bot = discord.Bot()

def main() -> None:
    load_dotenv()
    bot.run(os.getenv("TOKEN"))

if __name__ == "__main__":
    main()