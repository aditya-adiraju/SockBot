import discord
from database import get_target_info, create_db_connection, db_setup, add_initial_data , get_player_info, eliminate_player
from config import TOKEN, GUILD_IDS, YOU_HAVE_NO_ENEMIES
from logger import error, info, debug 
bot = discord.Bot()

@bot.event
async def on_ready():
    info(f"{bot.user} is ready and online!")

@bot.slash_command(guild_ids=GUILD_IDS, name="rules", description="The rules of the competition!")
async def rules(ctx: discord.ApplicationContext):
    with open('rules.md') as f:
        rules ='\n'.join(line.rstrip() for line in f)
    await ctx.respond(rules, ephemeral=True)

@bot.slash_command(guild_ids=GUILD_IDS, name="get-target", description="Tells you who your Target is")
async def target(ctx: discord.ApplicationContext):
    player_discord_id = ctx.author.name
    con = create_db_connection()
    if (target_info := get_target_info(con, player_discord_id)) is None:
        await ctx.respond(f"You have no enemies... It's over.\n\n\n{YOU_HAVE_NO_ENEMIES}", ephemeral=True)
        return
    target_id, target_name, group_name, _ = target_info
    if target_id == player_discord_id:
        await ctx.respond(f"# You win! \nyou have no enemies... It's over.\n\n\n{YOU_HAVE_NO_ENEMIES}", ephemeral=True)
        return
    await ctx.respond(f"Your target is {target_name} (discord: `@{target_id}`) from {group_name}", ephemeral=True)

@bot.slash_command(guild_ids=GUILD_IDS, name="get-secret", description="Tells you your Secret Word")
async def retrieve_secret_word(ctx: discord.ApplicationContext):
    player_discord_id = ctx.author.name
    con = create_db_connection()
    player_name, _, secret_word = get_player_info(con, player_discord_id)
    await ctx.respond(f"Hi {player_name}, Your Secret Word is ||{secret_word}||", ephemeral=True)

@bot.slash_command(guild_ids=GUILD_IDS, name="sock", description="Sock your target with their secret word!")
@discord.option("secret word", description="Your target's secret word")
async def sock_player(ctx: discord.ApplicationContext, secret_word: str):
    player_discord_id = ctx.author.name
    con = create_db_connection()

    if (player_info := get_player_info(con, player_discord_id)) is None:
        await ctx.respond(f"No such player exists: `@{player_discord_id}`", ephemeral=True)
        return
    player_name, _, _ = player_info

    if (target_info := get_target_info(con, player_discord_id)) is None:
        await ctx.respond(f"You have no enemies... It's over.\n\n\n{YOU_HAVE_NO_ENEMIES}", ephemeral=True)
        return
    target_id, target_name, _, target_secret_word = target_info

    if target_secret_word.strip().lower() == secret_word.strip().lower():
        eliminate_player(con, target_id)
        await ctx.send(f"{player_name} has successfully eliminated {target_name}!")
        await ctx.respond(f" Run `/get-target` to get your new target.", ephemeral=True)
    else:
        await ctx.respond(f"""Unfortunately, {secret_word} is not your target's secret word. Make sure you spell the secret word correctly. \n If you think there has been a mistake, contact an admin.
                          """, ephemeral=True)

def setup():
    con = create_db_connection()
    db_setup(con)
    add_initial_data(con, 'sockwars_initial_data.csv')

#setup()
bot.load_extension('cogs.admin')
bot.run(TOKEN)


