import discord
import os 
from dotenv import load_dotenv
from logger import error, info, debug 
load_dotenv() 
bot = discord.Bot()

@bot.event
async def on_ready():
    info(f"{bot.user} is ready and online!")

@bot.slash_command(name="hello", description="Say hello to the bot")
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")

bot.run(os.getenv('TOKEN'))


