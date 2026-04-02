from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ping", help="Check bot latency")
    async def ping(self, ctx):
        await ctx.send(f"Pong! Latency: {round(self.bot.latency * 1000)}ms")

    @commands.command(name="status", help="Check bot status")
    async def status(self, ctx):
        ping = round(self.bot.latency * 1000)
        dashboard = "https://discord-bot-rh78.onrender.com/status"
        msg = (
            f"Bot is currently running and operational!\n"
            f"Ping: {ping}ms\n"
            f"Status: Running\n"
            f"Check the dashboard for more details: "
            f"[ZioTikiBot Dashboard]({dashboard})"
        )
        await ctx.send(msg)

async def setup(bot):
    await bot.add_cog(General(bot))
