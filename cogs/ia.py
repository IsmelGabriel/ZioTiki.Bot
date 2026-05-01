import asyncio
import logging
import discord
from discord import app_commands
from discord.ext import commands
from utils.ia import generate_response
from utils.memory_db import clear_history
from utils.error_logs_db import log_ai_error

logger = logging.getLogger(__name__)

class IA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="ask", description="Talk to the AI.")
    @app_commands.checks.cooldown(1, 10, key=lambda i: (i.guild_id, i.user.id))
    async def ask(self, interaction: discord.Interaction, question: str):
        if len(question) > 300:
            await interaction.response.send_message("⚠️ Tu mensaje es muy largo. Máximo 300 caracteres.", ephemeral=True)
            return

        await interaction.response.defer()
        server_id = interaction.guild_id if interaction.guild else 0
        try:
            response = await asyncio.to_thread(
                generate_response, server_id, interaction.user.id, question
            )
            await interaction.followup.send(response)
        except Exception as e:
            log_ai_error(
                error_message=str(e),
                server_id=server_id,
                user_id=interaction.user.id
            )
            await interaction.followup.send(
                "❌ El sistema de IA no está disponible en este momento."
            )

    @app_commands.command(name="reset", description="Clear your conversation memory with the AI.")
    async def reset(self, interaction: discord.Interaction):
        server_id = interaction.guild_id if interaction.guild else 0
        clear_history(server_id, interaction.user.id)
        await interaction.response.send_message("🧠 Memory cleared successfully.")

async def setup(bot):
    await bot.add_cog(IA(bot))
