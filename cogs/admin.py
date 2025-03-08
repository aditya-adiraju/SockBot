from config import GUILD_IDS, YOU_HAVE_NO_ENEMIES
from database import create_db_connection, get_target_info, get_player_info, eliminate_player, undo_last_kill, roll_back_kills_to_id
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
            await ctx.respond(f"{player_name}'s secret word is ||{secret_word}||", ephemeral=True)

    @admin.command(name="sock", description="(admin) Eliminate a player")
    @discord.default_permissions(administrator=True)
    @option("player_discord_id", description="The player's discord id")
    async def sock_player(self, ctx: discord.ApplicationContext, player_discord_id: str):
        con = create_db_connection()
        if (player_info := get_player_info(con, player_discord_id)) is None:
            await ctx.respond(f"No such player exists: `@{player_discord_id}`", ephemeral=True)
            return
        player_name, _, _ = player_info
        kill_id = eliminate_player(con, player_discord_id)

        await ctx.respond(f"{player_name} has been socked! (kill ID: {kill_id})")

    @admin.command(name="undo-last-kill", description="(admin) Undoes last kill in the game")
    @discord.default_permissions(administrator=True)
    @option("are_you_really_sure", description="YES/NO (this action is irreversible!)")
    async def admin_undo_last_kill(self, ctx: discord.ApplicationContext, are_you_really_sure: str):
        if are_you_really_sure != "YES":
            await ctx.respond(f"you're not sure enough about this!, say YES or NO", ephemeral=True)
            return

        kill_info = undo_last_kill()
        if kill_info is None:
            await ctx.respond(f"No kills left to undo!", ephemeral=True)
            return

        kill_id, player_discord_id, eliminated_discord_id = kill_info
        await ctx.respond(f"`kill_id` {kill_id} has been Undone! (`@{player_discord_id}`'s elimination of `@{eliminated_discord_id}`)")

    @admin.command(name="rollback-kills", description="(admin) Undoes last kill in the game")
    @discord.default_permissions(administrator=True)
    @option("rollback_id", type=int, description="Kill ID to rollback to")
    @option("are_you_really_sure", description="YES/NO (this action is irreversible!)")
    async def admin_undo_last_kill(self, ctx: discord.ApplicationContext, rollback_id: int, are_you_really_sure: str):
        if are_you_really_sure != "YES":
            await ctx.respond(f"you're not sure enough about this!, say YES or NO", ephemeral=True)
            return

        reversed_kills = roll_back_kills_to_id(rollback_id)
        await ctx.respond(f"{reversed_kills} kills have been rolled back")

def setup(bot):
    bot.add_cog(Admin(bot))