import discord
from discord import app_commands
from discord.ext import commands
from utils.prompt_db import update_prompt

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _can_moderate(self, interaction: discord.Interaction, member: discord.Member) -> str | None:
        """Returns an error message if author cannot moderate member, else None."""
        if member == interaction.user:
            return "No puedes usar este comando sobre ti mismo."
        if member == interaction.guild.me:
            return "No puedes usar este comando sobre el bot."
        if member == interaction.guild.owner:
            return "No puedes usar este comando sobre el dueño del servidor."
        if interaction.user.top_role <= member.top_role and interaction.user != interaction.guild.owner:
            return "No puedes moderar a alguien con un rol igual o superior al tuyo."
        return None

    @app_commands.command(name="mute", description="Mute a user from server")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def mute(self, interaction: discord.Interaction, member: discord.Member):
        if reason := self._can_moderate(interaction, member):
            await interaction.response.send_message(f"❌ {reason}", ephemeral=True)
            return

        muted_role = discord.utils.get(interaction.guild.roles, name="MemMuted")
        if not muted_role:
            await interaction.response.defer()
            muted_role = await interaction.guild.create_role(name="MemMuted")
            for channel in interaction.guild.channels:
                await channel.set_permissions(
                    muted_role,
                    speak=False,
                    send_messages=False,
                    read_message_history=True,
                    read_messages=False
                    )
            await member.add_roles(muted_role)
            await interaction.followup.send(f"{member.mention} has been muted.")
        else:
            await member.add_roles(muted_role)
            await interaction.response.send_message(f"{member.mention} has been muted.")

    @app_commands.command(name="unmute", description="Unmute a user from server")
    @app_commands.checks.has_permissions(manage_roles=True)
    async def unmute(self, interaction: discord.Interaction, member: discord.Member):
        muted_role = discord.utils.get(interaction.guild.roles, name="MemMuted")
        if muted_role and muted_role in member.roles:
            await member.remove_roles(muted_role)
            await interaction.response.send_message(f"{member.mention} has been unmuted.")
        else:
            await interaction.response.send_message(f"{member.mention} isn't muted.", ephemeral=True)

    @app_commands.command(name="kick", description="Kick a member from server")
    @app_commands.checks.has_permissions(kick_members=True)
    async def kick(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if err := self._can_moderate(interaction, member):
            await interaction.response.send_message(f"❌ {err}", ephemeral=True)
            return
        await member.kick(reason=reason)
        await interaction.response.send_message(f"{member.mention} has been kicked.")

    @app_commands.command(name="ban", description="Ban a member from server")
    @app_commands.checks.has_permissions(ban_members=True)
    async def ban(self, interaction: discord.Interaction, member: discord.Member, reason: str = None):
        if err := self._can_moderate(interaction, member):
            await interaction.response.send_message(f"❌ {err}", ephemeral=True)
            return
        await member.ban(reason=reason)
        await interaction.response.send_message(f"{member.mention} has been banned.")

    @app_commands.command(name="setprompt", description="Set a custom AI prompt for this server.")
    @app_commands.checks.has_permissions(administrator=True)
    async def set_prompt(self, interaction: discord.Interaction, new_prompt: str):
        server_id = interaction.guild_id if interaction.guild else None
        server_name = interaction.guild.name if interaction.guild else "Direct Message"
        if update_prompt(server_id, server_name, new_prompt):
            await interaction.response.send_message("✅ Prompt actualizado para este servidor.")
        else:
            await interaction.response.send_message("❌ Error al actualizar el prompt.", ephemeral=True)

async def setup(bot):
    await bot.add_cog(Admin(bot))
