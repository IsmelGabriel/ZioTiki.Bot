import random
import discord
from discord import app_commands
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="chiste", description="Cuenta un chiste aleatorio")
    async def joke(self, interaction: discord.Interaction):
        jokes = [
            "¿Por qué el libro de matemáticas estaba triste? ¡Porque tenía muchos problemas!",
            "¿Qué le dijo un pez a otro pez? ¡Nada!",
            "¿Por qué los pájaros no usan Facebook? ¡Porque ya tienen Twitter!"
        ]
        joke = random.choice(jokes)
        await interaction.response.send_message(joke)

    @app_commands.command(name="roll", description="Lanza un dado de 6 caras")
    async def roll(self, interaction: discord.Interaction):
        result = random.randint(1, 6)
        await interaction.response.send_message(f"Has lanzado un dado y ha salido: {result}")

async def setup(bot):
    await bot.add_cog(Fun(bot))
