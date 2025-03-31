import discord
import random
from database import *
from config import TOKEN, GUILD_IDS, YOU_HAVE_NO_ENEMIES, ITS_JOEVER, ERROR_CHANNEL_ID, SOCKED_MESSAGE_TEMPLATES, KILL_CHANNEL_ID 
from logger import error, info, debug 

bot = discord.Bot()
FREE_FOR_ALL = True
@bot.event
async def on_ready():
    info(f"{bot.user} is ready and online!")

@bot.event
async def on_application_command_error(ctx: discord.ApplicationContext, err: Exception):
    await ctx.respond("Something went wrong... Ask an admin", ephemeral=True)
    err_msg = error(f"{type(err)=} {str(err)=}")
    channel = bot.get_channel(ERROR_CHANNEL_ID)
    if channel:
        await channel.send(f"```\n{err_msg}\n```")
    else:
        error(f"ERROR channel not found {ERROR_CHANNEL_ID}")
    raise err

@bot.slash_command(guild_ids=GUILD_IDS, name="rules", description="The rules of the competition!")
async def rules(ctx: discord.ApplicationContext):
    with open('rules.md') as f:
        rules ='\n'.join(line.rstrip() for line in f)
    await ctx.respond(rules, ephemeral=True)

@bot.slash_command(guild_ids=GUILD_IDS, name="get-target", description="Tells you who your Target is")
async def target(ctx: discord.ApplicationContext):
    WIN_MESSAGE = f"# You win! \nyou have no enemies... It's over.\n\n\n{YOU_HAVE_NO_ENEMIES}"
    LOSE_MESSAGE = f"# You've been eliminated! \n\n\n{ITS_JOEVER}"
    player_discord_id = ctx.author.name
    con = create_db_connection()
    if (target_info := get_target_info(con, player_discord_id)) is None:
        await ctx.respond(LOSE_MESSAGE, ephemeral=True)
        return
    target_id, target_name, group_name, _ = target_info
    if target_id == player_discord_id:
        await ctx.respond(WIN_MESSAGE, ephemeral=True)
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

    if FREE_FOR_ALL:
        is_eliminated = True
        player_name = ''
        if (all_players := get_all_players(con, active_players_only=True)) is None:
            await ctx.respond(f"No such player exists: `@{player_discord_id}`", ephemeral=True)
            return
        for player in all_players:
            if player.player_id == player_discord_id:
                is_eliminated = False 
                player_name = player.name
                break
        if is_eliminated:
            LOSE_MESSAGE = f"# You've been eliminated! \n\n\n{ITS_JOEVER}"
            await ctx.respond(LOSE_MESSAGE, ephemeral=True)
            return

    else: 
        if (player_info := get_player_info(con, player_discord_id)) is None:
            await ctx.respond(f"No such player exists: `@{player_discord_id}`", ephemeral=True)
            return

        player_name, _, _ = player_info

    if FREE_FOR_ALL:
        if (target_info := get_target_info_by_secret_word(con, secret_word)) is None:
            await ctx.respond(f"No player with secret: {secret_word}", ephemeral=True)
            return
    else:
        if (target_info := get_target_info(con, player_discord_id)) is None:
            await ctx.respond(f"You have no enemies... It's over.\n\n\n{YOU_HAVE_NO_ENEMIES}", ephemeral=True)
            return

    target_id, target_name, _, target_secret_word = target_info

    debug(target_info)
    if target_secret_word.strip().lower() == secret_word.strip().lower():
        kill_id = eliminate_player(con, target_id)

        kill_message = random.choice(SOCKED_MESSAGE_TEMPLATES).format(player=player_name, target=target_name) 
        kill_message += f"\n-# Kill ID: {kill_id}"

        channel = bot.get_channel(KILL_CHANNEL_ID)
        if channel:
            await channel.send(kill_message)
        else:
            await ctx.send(kill_message)

        await ctx.respond(f" Run `/get-target` to get your new target.", ephemeral=True)
    else:
        await ctx.respond(f"""Unfortunately, {secret_word} is not your target's secret word. Make sure you spell the secret word correctly. \n If you think there has been a mistake, contact an admin.
                          """, ephemeral=True)

def setup():
    con = create_db_connection()
    db_setup(con)

setup()
bot.load_extension('cogs.admin')
bot.load_extension('cogs.stat')
bot.run(TOKEN)


