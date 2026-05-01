"""Cog de Help personalizado — adaptado para Slash Commands."""

import discord
from discord import app_commands
from discord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    CATEGORIES = {
        "General": {"emoji": "📊", "color": discord.Color.blue(), "description": "Comandos generales del bot"},
        "Fun": {"emoji": "🎮", "color": discord.Color.magenta(), "description": "Comandos divertidos y entretenimiento"},
        "Admin": {"emoji": "🛡️", "color": discord.Color.red(), "description": "Comandos de administración y moderación"},
        "IA": {"emoji": "🤖", "color": discord.Color.green(), "description": "Inteligencia Artificial y conversaciones"},
        "Trivia": {"emoji": "🎯", "color": discord.Color.gold(), "description": "Juego de preguntas y respuestas"},
    }

    def _get_category_config(self, cog_name: str) -> dict:
        return self.CATEGORIES.get(cog_name, {
            "emoji": "📁", "color": discord.Color.greyple(), "description": "Otros comandos"
        })

    @app_commands.command(name="help", description="Muestra la ayuda y lista de comandos del bot.")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📚 Centro de Ayuda",
            description=(
                f"¡Hola **{interaction.user.display_name}**! El bot ahora funciona con Slash Commands.\n\n"
                f"**Tip:** Simplemente escribe `/` en el chat y aparecerá la lista de comandos disponibles, agrupados visualmente por Discord.\n"
            ),
            color=discord.Color.blurple(),
        )

        for cog_name, cog in sorted(self.bot.cogs.items()):
            if cog_name in ("CommandsError", "HelpCommand"):
                continue

            # Para slash commands
            app_cmds = cog.get_app_commands()
            if not app_cmds:
                continue

            config = self._get_category_config(cog_name)
            commands_preview = ", ".join(f"`/{cmd.name}`" for cmd in app_cmds)

            embed.add_field(
                name=f"{config['emoji']} {cog_name}",
                value=f"{config['description']}\n{commands_preview}",
                inline=False,
            )

        embed.set_footer(
            text=f"Solicitado por {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
