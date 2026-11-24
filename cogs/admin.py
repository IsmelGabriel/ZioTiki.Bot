import discord
from discord import app_commands
from discord.ext import commands
from utils.prompt_db import update_prompt
from bot import bot

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _can_moderate(self, interaction: discord.Interaction, member: discord.Member) -> str | None:
        """Returns an error message if author cannot moderate member, else None."""
        if member == interaction.user:
            return "You cannot use this command on yourself."
        if member == interaction.guild.me:
            return "You cannot use this command on the bot."
        if member == interaction.guild.owner:
            return "You cannot use this command on the server owner."
        if interaction.user.top_role <= member.top_role and interaction.user != interaction.guild.owner:
            return "You cannot moderate someone with a role equal to or higher than yours."
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
            permissions = discord.Permissions(send_messages=False, speak=False)
            muted_role = await interaction.guild.create_role(name="MemMuted", permissions=permissions)

            # Aplicar permisos por categoría (antes era por cada canal)
            for category in interaction.guild.categories:
                await category.set_permissions(
                    muted_role, speak=False, send_messages=False, read_message_history=True, read_messages=False
                )

            # Aplicar a canales sueltos
            for channel in interaction.guild.channels:
                if channel.category is None:
                    await channel.set_permissions(
                        muted_role, speak=False, send_messages=False, read_message_history=True, read_messages=False
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
            await interaction.response.send_message("✅ Prompt updated for this server.")
        else:
            await interaction.response.send_message("❌ Error updating the prompt.", ephemeral=True)

    @app_commands.command(name="update_announce", description="(Owner Only) Announce an update across all servers.")
    async def update_announce(self, interaction: discord.Interaction, version: str, notes: str):
        # 1. Verify that ONLY the bot owner can use this
        is_owner = await self.bot.is_owner(interaction.user)
        if not is_owner:
            await interaction.response.send_message("❌ Only the bot owner can use this command.", ephemeral=True)
            return

        await interaction.response.defer(ephemeral=True)

        # 2. Create announcement embed
        formatted_notes = notes.replace("\\n", "\n")

        embed = discord.Embed(
            title=f"🚀 System Update: v{version}",
            description=f"**Patch notes:**\n{formatted_notes}",
            color=discord.Color.brand_red()
        )
        embed.set_footer(text="ZioTiki Bot Core Update")

        servers_notified = 0

        # 3. Iterate through all guilds
        for guild in self.bot.guilds:
            target_channel = guild.system_channel

            if target_channel is None:
                for c in guild.text_channels:
                    # Find best channel to announce
                    if any(word in c.name.lower() for word in ["updates", "announcements", "news", "admin", "general", "actualizaciones", "noticias"]):
                        target_channel = c
                        break

            # 4. Send message if channel is found and bot has permissions
            if target_channel:
                try:
                    await target_channel.send(embed=embed)
                    servers_notified += 1
                except discord.Forbidden:
                    pass # Bot lacks permission to send messages in this channel

        await interaction.followup.send(f"✅ Update announcement (v{version}) successfully sent to **{servers_notified}** servers.")

async def setup(bot):
    await bot.add_cog(Admin(bot))
