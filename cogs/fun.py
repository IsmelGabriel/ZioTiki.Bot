import random
import discord
from discord import app_commands
from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command(name="joke", description="Tell a random joke")
    async def joke(self, interaction: discord.Interaction):
        jokes = [
            "Why was the math book sad? Because it had too many problems!",
            "What did one ocean say to the other ocean? Nothing, they just waved!",
            "Why don't scientists trust atoms? Because they make up everything!"
        ]
        joke = random.choice(jokes)
        await interaction.response.send_message(joke)

    @app_commands.command(name="roll", description="Roll a 6-sided die")
    async def roll(self, interaction: discord.Interaction):
        result = random.randint(1, 6)
        await interaction.response.send_message(f"You rolled a die and got: {result}")

async def setup(bot):
    await bot.add_cog(Fun(bot))
