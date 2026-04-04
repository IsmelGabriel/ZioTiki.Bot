from discord.ext import commands

class CommandsError(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        if getattr(error, "handled", False):
            return
        if isinstance(error, commands.CommandNotFound):
            prefix = ctx.prefix or "="
            await ctx.send(f"❌ Command not found. Type {prefix}help command for more info on a command.")
        elif isinstance(error, commands.MissingRequiredArgument):
            await ctx.send("❌ Command missing required arguments.")
        elif isinstance(error, commands.CommandOnCooldown):
            await ctx.send(f"⏳ Espera {error.retry_after:.0f}s antes de usar este comando de nuevo.")
        elif isinstance(error, commands.CheckFailure):
            await ctx.send("❌ You do not have permission to use this command.")
        else:
            await ctx.send("❌ An error occurred while processing the command.")
            raise error  # Re-raise the error for logging purposes

async def setup(bot):
    await bot.add_cog(CommandsError(bot))
