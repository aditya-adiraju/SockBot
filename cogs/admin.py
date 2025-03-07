from config import GUILD_IDS
from database import create_db_connection, get_target_info, get_player_info
from discord.ext import commands
from discord import Permissions, TextChannel
from discord.commands import option
from discord.utils import get
import discord

class Admin(commands.Cog):
    def __init__(self, bot: discord.Bot):
        self.bot = bot

    admin = discord.SlashCommandGroup('admin', 'Admin related commands', guild_ids=GUILD_IDS)

    @admin.command(name="target", description="(admin) Get a given player's target")
    @discord.default_permissions(administrator=True)
    @option("player_discord_id", description="The player's discord id")
    async def admin_get_target(self, ctx: discord.ApplicationContext, player_discord_id: str):
        player_discord_id = player_discord_id.strip()
        con = create_db_connection()
        player_info = get_player_info(con, player_discord_id)
        if player_info is None:
            await ctx.respond(f"No Player associated with {player_discord_id}")
            return
        player_name, _, _ = player_info
        target_info = get_target_info(con, player_discord_id)
        if target_info is None:
            await ctx.respond(f"No target associated with {player_discord_id}")
        else:
            target_id, target_name, group_name, secret_word = target_info
            await ctx.respond(f"{player_name}'s target is {target_name} (discord: `@{target_id}`) from {group_name}", ephemeral=True)
    
    @admin.command(name="secret-word", description="(admin) Get a given player's secret word")
    @discord.default_permissions(administrator=True)
    @option("player_discord_id", description="The player's discord id")
    async def admin_get_secret(self, ctx: discord.ApplicationContext, player_discord_id: str):
        player_discord_id = player_discord_id.strip()
        con = create_db_connection()
        player_info = get_player_info(con, player_discord_id)
        if player_info is None:
            await ctx.respond(f"No Player associated with {player_discord_id}")
        else:
            player_name, _, secret_word = player_info
            await ctx.respond(f"{player_name}'s secret word is {secret_word}", ephemeral=True)

def setup(bot):
    bot.add_cog(Admin(bot))