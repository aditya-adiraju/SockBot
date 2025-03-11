
from config import GUILD_IDS, YOU_HAVE_NO_ENEMIES
from database import *
from discord.ext import commands
from discord import Permissions, TextChannel
from discord.commands import option
from discord.utils import get
from datetime import datetime
from model import *
import discord



def _table_to_message(table_data, header):

    table = [f"{header.upper()}"]
    table.extend([str(row) for row in table_data])
    table_contents = ('\n'.join(table))[-1875:]
    message = f"```\n{table_contents}\n```"
    data = '\n'.join(table)
    while len(data) > 1875:
        table = [f"{header.upper()}"]
        table.extend([str(row) for row in table_data])
        table_contents = ('\n'.join(table))[-1875:]
        message = f"```\n{table_contents}\n```"
    return message

class Stat(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    stat = discord.SlashCommandGroup('stat', 'Statistical Summary Commands', guild_ids=GUILD_IDS)

    @stat.command(name="all-kills", description="(stat) Get all kills")
    async def all_kills(self, ctx: discord.ApplicationContext):
        con = create_db_connection()
        
        kills = get_all_kills(con)

        kill_message = _table_to_message(kills, KILL_ENTRY.HEADER)
        await ctx.respond(kill_message)

    @stat.command(name="daily-kills", description="(stat) Get kills from today")
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
        kill_message = _table_to_message(kills, KILL_ENTRY.HEADER)
        await ctx.respond(kill_message)

    @stat.command(name="weekly-kills", description="(stat) Get all kills between dates")
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
        kill_message = _table_to_message(kills, KILL_ENTRY.HEADER)
        await ctx.respond(kill_message)
    

    @stat.command(name="top-kills", description="(stat) Get a rollup of overall top players ordered by their kill count")
    async def top_kills(self, ctx: discord.ApplicationContext):
        con = create_db_connection()

        kill_summary = get_top_kills(con)
        message = _table_to_message(kill_summary, KILL_SUMMARY.HEADER)
        await ctx.respond(message)

    @stat.command(name="top-weekly-kills", description="(stat) Get a list of top players between dates")
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
        message = _table_to_message(kill_summary, KILL_SUMMARY.HEADER)
        await ctx.respond(message)

    @stat.command(name="top-daily-kills", description="(stat) Get a list of top players on a date (defualt today)")
    @option(name='date', description="(optional) provide a specific date (YYYY-MM-DD)", required=False)
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
        kill_message = _table_to_message(kills, KILL_SUMMARY.HEADER)
        await ctx.respond(kill_message)


    @stat.command(name="all-players", description="(stat) Get a list of all player and their elimination status.")
    async def all_players(self, ctx: discord.ApplicationContext):
        con = create_db_connection()
        player_summary = get_all_players(con)
        message = _table_to_message(player_summary, PLAYER.HEADER)
        await ctx.respond(message)

    @stat.command(name="target-assignments", description="(stat) Get a list of all target assignments")
    @discord.default_permissions(administrator=True)
    async def all_target_assignments(self, ctx: discord.ApplicationContext):
        con = create_db_connection()
        assignment_summary = get_target_assignments(con)
        message = _table_to_message(assignment_summary, TARGET_ASSIGNMENT.HEADER)
        await ctx.respond(message, ephemeral=True)

def setup(bot):
    bot.add_cog(Stat(bot))