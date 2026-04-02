import discord
from discord.ext import commands
from utils.prompt_db import update_prompt

class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    def _can_moderate(self, ctx, member: discord.Member) -> str | None:
        """Returns an error message if ctx.author cannot moderate member, else None."""
        if member == ctx.author:
            return "No puedes usar este comando sobre ti mismo."
        if member == ctx.guild.me:
            return "No puedes usar este comando sobre el bot."
        if member == ctx.guild.owner:
            return "No puedes usar este comando sobre el dueño del servidor."
        if ctx.author.top_role <= member.top_role and ctx.author != ctx.guild.owner:
            return "No puedes moderar a alguien con un rol igual o superior al tuyo."
        return None

    @commands.command(name="mute", help="Mute a user from server")
    @commands.has_permissions(manage_roles=True)
    async def mute(self, ctx, member: commands.MemberConverter):
        if reason := self._can_moderate(ctx, member):
            await ctx.send(f"❌ {reason}")
            return

        muted_role = discord.utils.get(ctx.guild.roles, name="MemMuted")
        if not muted_role:
            muted_role = await ctx.guild.create_role(name="MemMuted")
            for channel in ctx.guild.channels:
                await channel.set_permissions(
                    muted_role,
                    speak=False,
                    send_messages=False,
                    read_message_history=True,
                    read_messages=False
                    )

        await member.add_roles(muted_role)
        await ctx.send(f"{member.mention} has been muted.")

    @commands.command(name="unmute", help="Unmute a user from server")
    @commands.has_permissions(manage_roles=True)
    async def unmute(self, ctx, member: commands.MemberConverter):
        muted_role = discord.utils.get(ctx.guild.roles, name="MemMuted")
        if muted_role in member.roles:
            await member.remove_roles(muted_role)
            await ctx.send(f"{member.mention} has been unmuted.")
        else:
            await ctx.send(f"{member.mention} isn't muted.")

    @commands.command(name="kick", help="Kick a member from server")
    @commands.has_permissions(kick_members=True)
    async def kick(self, ctx, member: commands.MemberConverter, *, reason=None):
        if err := self._can_moderate(ctx, member):
            await ctx.send(f"❌ {err}")
            return
        await member.kick(reason=reason)
        await ctx.send(f"{member.mention} has been kicked.")

    @commands.command(name="ban", help="Ban a member from server")
    @commands.has_permissions(ban_members=True)
    async def ban(self, ctx, member: commands.MemberConverter, *, reason=None):
        if err := self._can_moderate(ctx, member):
            await ctx.send(f"❌ {err}")
            return
        await member.ban(reason=reason)
        await ctx.send(f"{member.mention} has been banned.")

    @commands.has_permissions(administrator=True)
    @commands.command(name="setprompt", help="Set a custom AI prompt for this server.")
    async def set_prompt(self, ctx, *, new_prompt: str):
        server_id = ctx.guild.id if ctx.guild else None
        server_name = ctx.guild.name if ctx.guild else "Direct Message"
        if update_prompt(server_id, server_name, new_prompt):
            await ctx.send("✅ Prompt actualizado para este servidor.")
        else:
            await ctx.send("❌ Error al actualizar el prompt.")

async def setup(bot):
    await bot.add_cog(Admin(bot))
