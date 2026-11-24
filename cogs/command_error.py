import discord
from discord import app_commands
from discord.ext import commands

class CommandsError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        # Registrar el manejador de errores para Slash Commands
        bot.tree.on_error = self.on_app_command_error

    async def on_app_command_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError):
        if isinstance(error, app_commands.CommandOnCooldown):
            msg = f"⏳ Please wait {error.retry_after:.1f}s before using this command again."
        elif isinstance(error, app_commands.MissingPermissions):
            msg = "❌ You do not have permission to use this command."
        elif isinstance(error, app_commands.BotMissingPermissions):
            msg = "❌ I do not have the required permissions to execute this command."
        elif isinstance(error, app_commands.CheckFailure):
            msg = "❌ You cannot use this command here or you do not meet the requirements."
        else:
            msg = "❌ An unexpected error occurred while processing the command."

        if interaction.response.is_done():
            await interaction.followup.send(msg, ephemeral=True)
        else:
            await interaction.response.send_message(msg, ephemeral=True)

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if getattr(error, "handled", False):
            return
        if isinstance(error, commands.CommandNotFound):
            prefix = ctx.prefix or "="
            await ctx.send(f"❌ The prefix '{prefix}' is disabled. Please use '/help' instead to see all commands.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Command is missing required arguments.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Please wait {error.retry_after:.0f}s before using this command again.")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You do not have permission to use this command.")
        else:
            await ctx.send("❌ An error occurred while processing the command.")
            raise error  # Re-raise the error for logging purposes

async def setup(bot):
    await bot.add_cog(CommandsError(bot))
