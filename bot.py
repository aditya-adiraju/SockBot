import discord
from database import get_target_info, create_db_connection, db_setup, add_initial_data , get_player_info
from config import TOKEN, GUILD_IDS
from logger import error, info, debug 
bot = discord.Bot()

@bot.event
async def on_ready():
    info(f"{bot.user} is ready and online!")

@bot.slash_command(name="hello", description="Say hello to the bot") 
async def hello(ctx: discord.ApplicationContext):
    await ctx.respond("Hey!")

@bot.slash_command(guild_ids=GUILD_IDS, name="get-target", description="Tells you who your Target is")
async def target(ctx: discord.ApplicationContext):
    player_discord_id = ctx.author.name
    con = create_db_connection()
    target_id, target_name, group_name, secret_word = get_target_info(con, player_discord_id)
    await ctx.respond(f"Your target is {target_name} (discord: `@{target_id}`) from {group_name}", ephemeral=True)

@bot.slash_command(guild_ids=GUILD_IDS, name="get-secret", description="Tells you your Secret Word")
async def retrieve_secret_word(ctx: discord.ApplicationContext):
    player_discord_id = ctx.author.name
    con = create_db_connection()
    player_name, group_name, secret_word = get_player_info(con, player_discord_id)
    await ctx.respond(f"Hi {player_name}, Your Secret Word is ||{secret_word}||", ephemeral=True)


def setup():
    con = create_db_connection()
    db_setup(con)
    add_initial_data(con, 'sockwars_initial_data.csv')

# setup()
bot.load_extension('cogs.admin')
bot.run(TOKEN)


