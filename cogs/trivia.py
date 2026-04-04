"""Cog de Trivia — juego de preguntas y respuestas por servidor."""

import asyncio
import logging

import discord
from discord.ext import commands

from utils.trivia_db import (
    add_points,
    add_question,
    delete_question,
    get_difficulties,
    get_difficulty_points,
    get_leaderboard,
    get_question_count,
    get_random_question,
    get_user_points,
    list_questions,
)

logger = logging.getLogger(__name__)

# Tiempo en segundos para responder una pregunta
ANSWER_TIMEOUT = 30

# Preguntas activas: {channel_id: question_dict}
_active_games: dict[int, dict] = {}


class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── Comandos de administrador ─────────────────────────────────────────────

    @commands.command(
        name="trivia_add",
        help="[Admin] Agrega una pregunta de trivia.\nUso: =trivia_add <dificultad> | <pregunta> | <respuesta>",
    )
    @commands.has_permissions(administrator=True)
    async def trivia_add(self, ctx, *, args: str):
        """Registra una pregunta. Formato: =trivia_add facil | ¿Cuánto es 2+2? | 4"""
        parts = [p.strip() for p in args.split("|")]
        if len(parts) != 3:
            await ctx.send(
                "❌ Formato incorrecto. Usa:\n"
                "`=trivia_add <dificultad> | <pregunta> | <respuesta>`\n"
                "Ejemplo: `=trivia_add facil | ¿Cuánto es 2+2? | 4`"
            )
            return

        difficulty, question, answer = parts

        if get_difficulty_points(difficulty) is None:
            diffs = ", ".join(f"`{d['name']}`" for d in get_difficulties())
            await ctx.send(f"❌ Dificultad `{difficulty}` no existe. Opciones: {diffs}")
            return

        if len(question) < 5:
            await ctx.send("❌ La pregunta es demasiado corta.")
            return

        if len(answer) < 1:
            await ctx.send("❌ La respuesta no puede estar vacía.")
            return

        if add_question(ctx.guild.id, question, answer, difficulty, ctx.author.id):
            points = get_difficulty_points(difficulty)
            await ctx.send(
                f"✅ Pregunta registrada.\n"
                f"**Dificultad:** {difficulty} ({points} pts)\n"
                f"**Q:** {question}\n"
                f"**R:** ||{answer}||"
            )
        else:
            await ctx.send("❌ Error al registrar la pregunta. Inténtalo de nuevo.")

    @commands.command(
        name="trivia_del",
        help="[Admin] Elimina una pregunta por ID.\nUso: =trivia_del <id>",
    )
    @commands.has_permissions(administrator=True)
    async def trivia_del(self, ctx, question_id: int):
        if delete_question(question_id, ctx.guild.id):
            await ctx.send(f"🗑️ Pregunta `#{question_id}` eliminada.")
        else:
            await ctx.send(f"❌ No se encontró la pregunta `#{question_id}` en este servidor.")

    @commands.command(
        name="trivia_list",
        help="[Admin] Lista las últimas 10 preguntas registradas en este servidor.",
    )
    @commands.has_permissions(administrator=True)
    async def trivia_list(self, ctx):
        questions = list_questions(ctx.guild.id)
        if not questions:
            await ctx.send("📭 No hay preguntas registradas en este servidor.")
            return

        lines = [f"`#{q['id']}` [{q['difficulty']}] {q['question']}" for q in questions]
        embed = discord.Embed(
            title="📋 Preguntas de Trivia",
            description="\n".join(lines),
            color=discord.Color.blue(),
        )
        embed.set_footer(text=f"Total: {get_question_count(ctx.guild.id)} preguntas")
        await ctx.send(embed=embed)

    # ── Comandos de juego ─────────────────────────────────────────────────────

    @commands.command(
        name="trivia",
        help="Inicia una pregunta de trivia.",
    )
    async def trivia(self, ctx):
        if ctx.channel.id in _active_games:
            await ctx.send("⚠️ Ya hay una pregunta activa en este canal. ¡Respóndela primero!")
            return

        question = get_random_question(ctx.guild.id)
        if not question:
            await ctx.send(
                "📭 No hay preguntas registradas en este servidor.\n"
                "Contacta a un administrador para que agregue algunas preguntas y respuestas."
            )
            return

        _active_games[ctx.channel.id] = question

        embed = discord.Embed(
            title="🎯 Trivia",
            description=question["question"],
            color=discord.Color.gold(),
        )
        embed.add_field(name="Dificultad", value=f"{question['difficulty']} (+{question['points']} pts)")
        embed.set_footer(text=f"Tienes {ANSWER_TIMEOUT} segundos para responder.")
        await ctx.send(embed=embed)

        def check(msg: discord.Message) -> bool:
            return (
                msg.channel.id == ctx.channel.id
                and not msg.author.bot
                and msg.content.lower().strip() == question["answer"]
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=ANSWER_TIMEOUT)
            _active_games.pop(ctx.channel.id, None)

            add_points(ctx.guild.id, msg.author.id, question["points"])
            total = get_user_points(ctx.guild.id, msg.author.id)

            embed_win = discord.Embed(
                title="✅ ¡Correcto!",
                description=f"{msg.author.mention} acertó la respuesta: **{question['answer']}**",
                color=discord.Color.green(),
            )
            embed_win.add_field(name="Puntos ganados", value=f"+{question['points']} pts")
            embed_win.add_field(name="Puntos totales", value=f"{total} pts")
            await ctx.send(embed=embed_win)

        except asyncio.TimeoutError:
            _active_games.pop(ctx.channel.id, None)
            await ctx.send(
                f"⏰ ¡Se acabó el tiempo! La respuesta era: **{question['answer']}**"
            )

    @commands.command(
        name="trivia_top",
        help="Muestra el ranking de puntos de trivia en este servidor.",
    )
    async def trivia_top(self, ctx):
        leaderboard = get_leaderboard(ctx.guild.id)
        if not leaderboard:
            await ctx.send("📭 Aún no hay puntos registrados en este servidor.")
            return

        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for i, row in enumerate(leaderboard):
            user = ctx.guild.get_member(row["user_id"])
            name = user.display_name if user else f"Usuario {row['user_id']}"
            prefix = medals[i] if i < 3 else f"`{i+1}.`"
            lines.append(f"{prefix} **{name}** — {row['points']} pts")

        embed = discord.Embed(
            title="🏆 Ranking de Trivia",
            description="\n".join(lines),
            color=discord.Color.gold(),
        )
        await ctx.send(embed=embed)

    @commands.command(
        name="trivia_puntos",
        help="Muestra tus puntos de trivia en este servidor.",
    )
    async def trivia_puntos(self, ctx, member: discord.Member | None = None):
        target = member or ctx.author
        points = get_user_points(ctx.guild.id, target.id)
        await ctx.send(f"🎯 **{target.display_name}** tiene **{points} puntos** de trivia en este servidor.")

    @commands.command(
        name="trivia_dificultades",
        help="Muestra las dificultades disponibles y sus puntos.",
    )
    async def trivia_dificultades(self, ctx):
        diffs = get_difficulties()
        if not diffs:
            await ctx.send("❌ No hay dificultades configuradas.")
            return
        lines = [f"**{d['name']}** → {d['points']} puntos" for d in diffs]
        embed = discord.Embed(
            title="📊 Dificultades de Trivia",
            description="\n".join(lines),
            color=discord.Color.blurple(),
        )
        await ctx.send(embed=embed)


    # ── Manejo de errores del cog ─────────────────────────────────────────────

    _USAGE = {
        "trivia_add": (
            "`=trivia_add <dificultad> | <pregunta> | <respuesta>`\n"
            "Ejemplo: `=trivia_add facil | ¿Cuánto es 2+2? | 4`\n"
            "Dificultades: `facil`, `medio`, `dificil`"
        ),
        "trivia_del": (
            "`=trivia_del <id>`\n"
            "Ejemplo: `=trivia_del 12`\n"
            "Usa `=trivia_list` para ver los IDs de las preguntas."
        ),
        "trivia_puntos": (
            "`=trivia_puntos` — muestra tus puntos\n"
            "`=trivia_puntos @usuario` — muestra los puntos de otro usuario"
        ),
    }

    async def cog_command_error(self, ctx, error):
        # Desenvuelve errores encapsulados por discord.py
        error = getattr(error, "original", error)

        command_name = ctx.command.name if ctx.command else ""
        usage = self._USAGE.get(command_name)

        if isinstance(error, commands.MissingRequiredArgument):
            msg = f"❌ Argumentos faltantes:`."
            if usage:
                msg += f"\n\n📌 **Uso correcto:**\n{usage}"
            await ctx.send(msg)
            error.handled = True

        elif isinstance(error, commands.BadArgument):
            msg = "❌ Argumento inválido."
            if usage:
                msg += f"\n\n📌 **Uso correcto:**\n{usage}"
            await ctx.send(msg)
            error.handled = True

        elif isinstance(error, commands.MissingPermissions):
            await ctx.send("🔒 No tienes permisos de administrador para usar este comando.")
            error.handled = True

        else:
            # Deja que el manejador global lo tome
            raise error


async def setup(bot):
    await bot.add_cog(Trivia(bot))
