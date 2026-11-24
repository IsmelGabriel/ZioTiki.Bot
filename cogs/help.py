"""Cog de Help personalizado — adaptado para Slash Commands."""

import discord
from discord import app_commands
from discord.ext import commands

class HelpCommand(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    CATEGORIES = {
        "General": {"emoji": "📊", "color": discord.Color.blue(), "description": "General bot commands"},
        "Fun": {"emoji": "🎮", "color": discord.Color.magenta(), "description": "Fun and entertainment commands"},
        "Admin": {"emoji": "🛡️", "color": discord.Color.red(), "description": "Administration and moderation commands"},
        "IA": {"emoji": "🤖", "color": discord.Color.green(), "description": "Artificial Intelligence and conversations"},
        "Trivia": {"emoji": "🎯", "color": discord.Color.gold(), "description": "Trivia question and answer game"},
    }

    def _get_category_config(self, cog_name: str) -> dict:
        return self.CATEGORIES.get(cog_name, {
            "emoji": "📁", "color": discord.Color.greyple(), "description": "Other commands"
        })

    @app_commands.command(name="help", description="Displays help and command list for the bot.")
    async def help_command(self, interaction: discord.Interaction):
        embed = discord.Embed(
            title="📚 Help Center",
            description=(
                f"Hello **{interaction.user.display_name}**! The bot now uses Slash Commands.\n\n"
                f"**Tip:** Simply type `/` in chat to see all available commands, grouped visually by Discord.\n"
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
            text=f"Requested by {interaction.user.display_name}",
            icon_url=interaction.user.display_avatar.url,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
