import random

from discord.ext import commands

class Fun(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(name="chiste", help="Cuenta un chiste aleatorio")
    async def joke(self, ctx):
        jokes = [
            "¿Por qué el libro de matemáticas estaba triste? ¡Porque tenía muchos problemas!",
            "¿Qué le dijo un pez a otro pez? ¡Nada!",
            "¿Por qué los pájaros no usan Facebook? ¡Porque ya tienen Twitter!"
        ]
        joke = random.choice(jokes)
        await ctx.send(joke)

    @commands.command(name="roll", help="Lanza un dado de 6 caras")
    async def roll(self, ctx):
        result = random.randint(1, 6)
        await ctx.send(f"Has lanzado un dado y ha salido: {result}")

async def setup(bot):
    await bot.add_cog(Fun(bot))
