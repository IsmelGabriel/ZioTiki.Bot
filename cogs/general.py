import discord
from discord import app_commands
from discord.ext import commands

class General(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ping", description="Check bot latency")
    async def ping(self, interaction: discord.Interaction):
        await interaction.response.send_message(f"Pong! Latency: {round(self.bot.latency * 1000)}ms")

    @app_commands.command(name="status", description="Check bot status")
    async def status(self, interaction: discord.Interaction):
        ping = round(self.bot.latency * 1000)
        dashboard = "https://discord-bot-rh78.onrender.com/status"
        msg = (
            f"Bot is currently running and operational!\n"
            f"Ping: {ping}ms\n"
            f"Status: Running\n"
            f"Check the dashboard for more details: "
            f"[ZioTikiBot Dashboard]({dashboard})"
        )
        await interaction.response.send_message(msg)

async def setup(bot):
    await bot.add_cog(General(bot))
