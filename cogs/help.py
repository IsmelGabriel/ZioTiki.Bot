"""Cog de Help personalizado — comando de ayuda mejorado con embeds."""

import discord
from discord.ext import commands


class HelpCommand(commands.Cog):
    """Sistema de ayuda personalizado con embeds bonitos."""

    def __init__(self, bot):
        self.bot = bot

    # Configuración de categorías con emojis y colores
    CATEGORIES = {
        "General": {
            "emoji": "📊",
            "color": discord.Color.blue(),
            "description": "Comandos generales del bot",
        },
        "Fun": {
            "emoji": "🎮",
            "color": discord.Color.magenta(),
            "description": "Comandos divertidos y entretenimiento",
        },
        "Admin": {
            "emoji": "🛡️",
            "color": discord.Color.red(),
            "description": "Comandos de administración y moderación",
        },
        "IA": {
            "emoji": "🤖",
            "color": discord.Color.green(),
            "description": "Inteligencia Artificial y conversaciones",
        },
        "Trivia": {
            "emoji": "🎯",
            "color": discord.Color.gold(),
            "description": "Juego de preguntas y respuestas",
        },
    }

    def _get_category_config(self, cog_name: str) -> dict:
        """Obtiene la configuración de una categoría o devuelve valores por defecto."""
        return self.CATEGORIES.get(cog_name, {
            "emoji": "📁",
            "color": discord.Color.greyple(),
            "description": "Otros comandos",
        })

    @commands.command(name="help", aliases=["h", "ayuda", "comandos"])
    async def help_command(self, ctx, *, command_or_category: str = None):
        """
        Muestra la ayuda del bot.

        Uso:
        • =help — Ver todas las categorías
        • =help <categoría> — Ver comandos de una categoría
        • =help <comando> — Ver detalles de un comando
        """
        prefix = ctx.prefix or "="

        # Sin argumentos: mostrar menú principal
        if not command_or_category:
            await self._send_main_menu(ctx, prefix)
            return

        query = command_or_category.lower()

        # Buscar si es un comando
        cmd = self.bot.get_command(query)
        if cmd:
            await self._send_command_help(ctx, cmd, prefix)
            return

        # Buscar si es una categoría (cog)
        for cog_name, cog in self.bot.cogs.items():
            if cog_name.lower() == query:
                await self._send_category_help(ctx, cog_name, cog, prefix)
                return

        # No encontrado
        embed = discord.Embed(
            title="❌ No encontrado",
            description=f"No se encontró el comando o categoría `{command_or_category}`.\n"
                        f"Usa `{prefix}help` para ver todas las opciones.",
            color=discord.Color.red(),
        )
        await ctx.send(embed=embed)

    async def _send_main_menu(self, ctx, prefix: str):
        """Envía el menú principal con todas las categorías."""
        embed = discord.Embed(
            title="📚 Centro de Ayuda",
            description=(
                f"¡Hola **{ctx.author.display_name}**! Aquí están todas las categorías disponibles.\n\n"
                f"**Prefijo:** `{prefix}`\n"
                f"**Tip:** Usa `{prefix}help <categoría>` para ver los comandos de esa categoría.\n"
                f"**Tip:** Usa `{prefix}help <comando>` para ver detalles de un comando específico."
            ),
            color=discord.Color.blurple(),
        )

        # Obtener cogs con comandos visibles
        for cog_name, cog in sorted(self.bot.cogs.items()):
            # Ignorar cogs sin comandos o cogs internos
            if cog_name in ("CommandsError", "HelpCommand"):
                continue

            commands_list = [cmd for cmd in cog.get_commands() if not cmd.hidden]
            if not commands_list:
                continue

            config = self._get_category_config(cog_name)
            commands_preview = ", ".join(f"`{cmd.name}`" for cmd in commands_list[:5])
            if len(commands_list) > 5:
                commands_preview += f" y {len(commands_list) - 5} más..."

            embed.add_field(
                name=f"{config['emoji']} {cog_name}",
                value=f"{config['description']}\n{commands_preview}",
                inline=False,
            )

        embed.set_footer(
            text=f"Solicitado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )
        embed.set_thumbnail(url=self.bot.user.display_avatar.url)

        await ctx.send(embed=embed)

    async def _send_category_help(self, ctx, cog_name: str, cog, prefix: str):
        """Envía la ayuda de una categoría específica."""
        config = self._get_category_config(cog_name)
        commands_list = [cmd for cmd in cog.get_commands() if not cmd.hidden]

        embed = discord.Embed(
            title=f"{config['emoji']} Categoría: {cog_name}",
            description=config['description'],
            color=config['color'],
        )

        for cmd in commands_list:
            # Obtener el texto de ayuda del comando
            help_text = cmd.help or "Sin descripción"
            # Limitar a la primera línea para el resumen
            short_help = help_text.split('\n')[0]

            # Mostrar alias si existen
            alias_text = ""
            if cmd.aliases:
                alias_text = f"\n*Alias:* {', '.join(f'`{a}`' for a in cmd.aliases)}"

            embed.add_field(
                name=f"`{prefix}{cmd.name}`",
                value=f"{short_help}{alias_text}",
                inline=False,
            )

        embed.set_footer(
            text=f"Usa {prefix}help <comando> para más detalles | Solicitado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        # Añadir botón visual de "volver"
        embed.add_field(
            name="━━━━━━━━━━━━━━━━━━━━━",
            value=f"🔙 `{prefix}help` — Volver al menú principal",
            inline=False,
        )

        await ctx.send(embed=embed)

    async def _send_command_help(self, ctx, cmd: commands.Command, prefix: str):
        """Envía la ayuda detallada de un comando específico."""
        # Obtener el cog del comando para el color
        cog_name = cmd.cog_name or "General"
        config = self._get_category_config(cog_name)

        embed = discord.Embed(
            title=f"🔍 Comando: {cmd.name}",
            color=config['color'],
        )

        # Descripción del comando
        help_text = cmd.help or "Sin descripción disponible"
        embed.add_field(
            name="📝 Descripción",
            value=help_text,
            inline=False,
        )

        # Uso del comando
        signature = f"{prefix}{cmd.name}"
        if cmd.signature:
            signature += f" {cmd.signature}"
        embed.add_field(
            name="⚙️ Uso",
            value=f"`{signature}`",
            inline=False,
        )

        # Alias
        if cmd.aliases:
            aliases = ", ".join(f"`{prefix}{alias}`" for alias in cmd.aliases)
            embed.add_field(
                name="🔗 Alias",
                value=aliases,
                inline=True,
            )

        # Categoría
        embed.add_field(
            name="📁 Categoría",
            value=f"{config['emoji']} {cog_name}",
            inline=True,
        )

        # Cooldown si existe
        if cmd._buckets and cmd._buckets._cooldown:
            cooldown = cmd._buckets._cooldown
            embed.add_field(
                name="⏱️ Cooldown",
                value=f"{cooldown.rate} uso(s) cada {cooldown.per:.0f}s",
                inline=True,
            )

        # Permisos requeridos
        if cmd.checks:
            perms = self._get_permissions_from_checks(cmd.checks)
            if perms:
                embed.add_field(
                    name="🔒 Permisos requeridos",
                    value=perms,
                    inline=False,
                )

        embed.set_footer(
            text=f"<> = obligatorio | [] = opcional | Solicitado por {ctx.author.display_name}",
            icon_url=ctx.author.display_avatar.url,
        )

        # Navegación
        embed.add_field(
            name="━━━━━━━━━━━━━━━━━━━━━",
            value=f"🔙 `{prefix}help {cog_name}` — Ver categoría\n"
                  f"🏠 `{prefix}help` — Menú principal",
            inline=False,
        )

        await ctx.send(embed=embed)

    def _get_permissions_from_checks(self, checks) -> str:
        """Extrae los permisos requeridos de los checks del comando."""
        permissions = []
        perm_names = {
            "administrator": "Administrador",
            "manage_roles": "Gestionar roles",
            "kick_members": "Expulsar miembros",
            "ban_members": "Banear miembros",
            "manage_messages": "Gestionar mensajes",
            "manage_channels": "Gestionar canales",
            "manage_guild": "Gestionar servidor",
        }

        for check in checks:
            # Intentar obtener el nombre de la función del check
            check_name = getattr(check, "__qualname__", "")
            if "has_permissions" in check_name:
                # Buscar en los permisos conocidos
                for perm_key, perm_display in perm_names.items():
                    if perm_key in str(check.__code__.co_freevars) or perm_key in str(getattr(check, '__closure__', '')):
                        permissions.append(f"• {perm_display}")

        # Si no pudimos extraer permisos específicos pero hay checks
        if not permissions and checks:
            return "• Requiere permisos especiales"

        return "\n".join(permissions) if permissions else ""


async def setup(bot):
    await bot.add_cog(HelpCommand(bot))
