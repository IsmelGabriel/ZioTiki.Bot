import asyncio
import logging

from discord.ext import commands
from utils.ia import generate_response
from utils.memory_db import clear_history
from utils.error_logs_db import log_ai_error

logger = logging.getLogger(__name__)


class IA(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="ask", help="Talk to the AI.")
    @commands.cooldown(1, 10, commands.BucketType.user)
    async def ask(self, ctx, *, question: str):
        if len(question) > 300:
            await ctx.send("⚠️ Tu mensaje es muy largo. Máximo 300 caracteres.")
            return

        async with ctx.typing():
            server_id = ctx.guild.id if ctx.guild else 0
            try:
                response = await asyncio.to_thread(
                    generate_response, server_id, ctx.author.id, question
                )
                await ctx.send(response)
            except Exception as e:
                log_ai_error(
                    error_message=str(e),
                    server_id=server_id,
                    user_id=ctx.author.id
                )
                await ctx.send(
                    "❌ El sistema de IA no está disponible en este momento."
                )

    @commands.command(name="reset", help="Clear your conversation memory with the AI.")
    async def reset(self, ctx):
        server_id = ctx.guild.id if ctx.guild else 0
        clear_history(server_id, ctx.author.id)
        await ctx.send("🧠 Memory cleared successfully.")

async def setup(bot):
    await bot.add_cog(IA(bot))
