from config import GUILD_IDS, YOU_HAVE_NO_ENEMIES
from database import *
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
            await ctx.respond(f"No Player associated with {player_discord_id}", ephemeral=True)
            return
        player_name, _, _ = player_info
        target_info = get_target_info(con, player_discord_id)
        if target_info is None:
            await ctx.respond(f"No target associated with {player_discord_id}", ephemeral=True)
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
            await ctx.respond(f"No Player associated with {player_discord_id}", ephemeral=True)
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

    @admin.command(guild_ids=GUILD_IDS, name="ingest-csv", description="(admin) Add initial game data from CSV")
    @discord.default_permissions(administrator=True)
    @option("are_you_really_sure", description="YES/NO (this action is irreversible!)", )
    @option("m_id", description="Message ID")
    async def admin_ingest_csv(self, ctx: discord.ApplicationContext, message_id: str, are_you_really_sure: str):
        if are_you_really_sure != "YES":
            await ctx.respond(f"you're not sure enough about this!, say YES or NO", ephemeral=True)
            return
        try:
            message = await ctx.fetch_message(int(message_id))
            attachment = await message.attachments[0].read()
            with open(f'./data/{message_id}.csv', 'wb') as f:
                f.write(attachment)

            con = create_db_connection()
            add_initial_data(con, f'./data/{message_id}.csv')
            await ctx.respond(f"Game data has been retrieved from {message_id}")
        except:
            await ctx.respond("Something went wrong with this....", ephemeral=True)

    @admin.command(guild_ids=GUILD_IDS, name="delete-game-data", description="(admin) [**DONT TOUCH. BREAK GLASS**] Remove all rows in database")
    @discord.default_permissions(administrator=True)
    @option("are_you_really_sure", description="YES/NO (this action is irreversible!)", )
    @option("actually_sure", description="actually sure?")
    async def admin_ingest_csv(self, ctx: discord.ApplicationContext, are_you_really_sure: str, actually_sure: str):
        if are_you_really_sure != "YES" and actually_sure != "YES":
            await ctx.respond(f"you're not sure enough about this!, say YES or NO", ephemeral=True)
            return
        try:
            con = create_db_connection()
            delete_all_data(con)
            await ctx.respond("Done!")
        except:
            await ctx.respond("Something went wrong with this....", ephemeral=True)

    @admin.command(name="reset-secret", description="(admin) Reset a given player's secret word")
    @discord.default_permissions(administrator=True)
    @option("player_discord_id", description="The player's discord id")
    @option("new_secret_word", description="The new secret word")
    async def admin_reset_secret(self, ctx: discord.ApplicationContext, player_discord_id: str, new_secret_word: str):
        
        con = create_db_connection()
        old_secret_word = set_player_secret_word(con, player_discord_id, new_secret_word)
        if old_secret_word is None:
            await ctx.respond(f"No Player associated with {player_discord_id}", ephemeral=True)
            return
        else:
            await ctx.respond(f"{player_discord_id}'s secret word has been changed to ||{new_secret_word}|| (from ||{old_secret_word}||)", ephemeral=True)

def setup(bot):
    bot.add_cog(Admin(bot))