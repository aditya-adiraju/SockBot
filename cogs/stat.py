
from config import GUILD_IDS, YOU_HAVE_NO_ENEMIES
from database import *
from discord.ext import commands
from discord import Permissions, TextChannel
from discord.commands import option
from discord.utils import get
from datetime import datetime
from model import *
import discord


def _split_lines(lines, N):
    assert N > 1000

    chunk = ""
    chunks = []
    
    for line in lines:
        if len(chunk) + len(line) + 1 > N:
            chunks.append(chunk)
            chunk = ''
        chunk += line + '\n'

    chunks.append(chunk)

    return chunks

def _table_to_message(table_data, header) -> list[str]:
    table_data = [str(d) for d in table_data]
    chunks = _split_lines(table_data, 1875)
    messages = [f"```\n{header.upper()}\n{chunk}\n```" for chunk in chunks]
    return messages

class Stat(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    @commands.slash_command(guild_ids=GUILD_IDS, name="stat-all-kills", description="(stat) Get all kills")
    async def all_kills(self, ctx: discord.ApplicationContext):
        con = create_db_connection()
        
        kills = get_all_kills(con)

        kill_messages = _table_to_message(kills, KILL_ENTRY.HEADER)
        await ctx.respond(kill_messages[0])
        for m in kill_messages[1:]:
            await ctx.send(m)

    @commands.slash_command(guild_ids=GUILD_IDS, name="stat-daily-kills", description="(stat)(admin) Get kills from today")
    @option(name='date', description="(optional) provide a specific date (YYYY-MM-DD)", required=False)
    @discord.default_permissions(administrator=True)
    async def daily_kills(self, ctx: discord.ApplicationContext, date: str = ''):
        con = create_db_connection()
        try:
            if date.strip() == '': 
                date = datetime.now()
            else:
                date = datetime.strptime(date, '%Y-%m-%d')
        except:
            await ctx.respond(f"ERROR: you must provide valid date in YYYY-MM-DD format (no spaces!)", ephemeral=True)
            return

        kills = get_kills_on_date(con, date)
        kill_messages = _table_to_message(kills, KILL_ENTRY.HEADER)
        await ctx.respond(kill_messages[0])
        for m in kill_messages[1:]:
            await ctx.send(m)

    @commands.slash_command(guild_ids=GUILD_IDS, name="stat-weekly-kills", description="(stat)(admin) Get all kills between dates")
    @option(name='start_date', description="(optional) provide a specific date (YYYY-MM-DD)", required=True)
    @option(name='end_date', description="(optional) provide a specific date (YYYY-MM-DD)", required=False)
    @discord.default_permissions(administrator=True)
    async def weekly_kills(self, ctx: discord.ApplicationContext, start_date: str, end_date: str = ""):
        con = create_db_connection()
        try:
            start_date = datetime.strptime(start_date.strip(), '%Y-%m-%d')
            end_date = None if end_date.strip() == '' else datetime.strptime(end_date.strip(), '%Y-%m-%d')
        except:
            await ctx.respond(f"ERROR: you must provide valid date in YYYY-MM-DD format (no spaces!)", ephemeral=True)
            return

        kills = get_kills_between_dates(con, start_date, end_date)
        kill_messages = _table_to_message(kills, KILL_ENTRY.HEADER)
        await ctx.respond(kill_messages[0])
        for m in kill_messages[1:]:
            await ctx.send(m)
    

    @commands.slash_command(guild_ids=GUILD_IDS, name="stat-top-kills", description="(stat) Get a rollup of overall top players ordered by their kill count")
    async def top_kills(self, ctx: discord.ApplicationContext):
        con = create_db_connection()

        kill_summary = get_top_kills(con)
        messages = _table_to_message(kill_summary, KILL_SUMMARY.HEADER)

        await ctx.respond(messages[0])
        for m in messages[1:]:
            await ctx.send(m)

    @commands.slash_command(guild_ids=GUILD_IDS, name="stat-top-weekly-kills", description="(stat)(admin) Get a list of top players between dates")
    @option(name='start_date', description="(optional) provide a specific date (YYYY-MM-DD)", required=True)
    @option(name='end_date', description="(optional) provide a specific date (YYYY-MM-DD)", required=False)
    @discord.default_permissions(administrator=True)
    async def top_weekly_kills(self, ctx: discord.ApplicationContext, start_date: str, end_date: str = ""):
        con = create_db_connection()
        try:
            start_date = datetime.strptime(start_date.strip(), '%Y-%m-%d')
            end_date = None if end_date.strip() == '' else datetime.strptime(end_date.strip(), '%Y-%m-%d')
        except:
            await ctx.respond(f"ERROR: you must provide valid date in YYYY-MM-DD format (no spaces!)", ephemeral=True)
            return

        kill_summary = get_top_kills_between_dates(con, start_date, end_date)
        messages = _table_to_message(kill_summary, KILL_SUMMARY.HEADER)
        await ctx.respond(messages[0])
        for m in messages[1:]:
            await ctx.send(m)

    @commands.slash_command(guild_ids=GUILD_IDS, name="stat-top-daily-kills", description="(stat)(admin) Get a list of top players on a date (defualt today)")
    @option(name='date', description="(optional) provide a specific date (YYYY-MM-DD)", required=False)
    @discord.default_permissions(administrator=True)
    async def top_daily_kills(self, ctx: discord.ApplicationContext, date: str = ''):
        con = create_db_connection()
        try:
            if date.strip() == '': 
                date = datetime.now()
            else:
                date = datetime.strptime(date, '%Y-%m-%d')
        except:
            await ctx.respond(f"ERROR: you must provide valid date in YYYY-MM-DD format (no spaces!)", ephemeral=True)
            return

        kills = get_top_kills_on_date(con, date)
        messages = _table_to_message(kills, KILL_SUMMARY.HEADER)

        await ctx.respond(messages[0])
        for m in messages[1:]:
            await ctx.send(m)


    @commands.slash_command(guild_ids=GUILD_IDS, name="stat-all-players", description="(stat) Get a list of all player and their elimination status.")
    async def all_players(self, ctx: discord.ApplicationContext):
        con = create_db_connection()
        player_summary = get_all_players(con)
        messages = _table_to_message(player_summary, PLAYER.HEADER)
        await ctx.respond(messages[0])
        for m in messages[1:]:
            await ctx.send(m)

    @commands.slash_command(guild_ids=GUILD_IDS, name="stat-target-assignments", description="(stat)(admin) Get a list of all target assignments")
    @discord.default_permissions(administrator=True)
    async def all_target_assignments(self, ctx: discord.ApplicationContext):
        con = create_db_connection()
        assignment_summary = get_target_assignments(con)
        messages = _table_to_message(assignment_summary, TARGET_ASSIGNMENT.HEADER)
        await ctx.respond(messages[0], ephemeral=True)
        for m in messages[1:]:
            await ctx.send(m)

def setup(bot):
    bot.add_cog(Stat(bot))
