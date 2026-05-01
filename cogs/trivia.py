"""Cog de Trivia — juego de preguntas y respuestas por servidor."""

import asyncio
import logging

import discord
from discord import app_commands
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

ANSWER_TIMEOUT = 30
_active_games: dict[int, dict] = {}

class Trivia(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # ── Comandos de administrador ─────────────────────────────────────────────
    @app_commands.command(name="trivia_add", description="[Admin] Agrega una pregunta. d: facil/medio/dificil")
    @app_commands.checks.has_permissions(administrator=True)
    async def trivia_add(self, interaction: discord.Interaction, dificultad: str, pregunta: str, respuesta: str):
        if get_difficulty_points(dificultad.lower()) is None:
            diffs = ", ".join(f"`{d['name']}`" for d in get_difficulties())
            await interaction.response.send_message(f"❌ Dificultad `{dificultad}` no existe. Opciones: {diffs}", ephemeral=True)
            return

        if len(pregunta) < 5:
            await interaction.response.send_message("❌ La pregunta es demasiado corta.", ephemeral=True)
            return

        if len(respuesta) < 1:
            await interaction.response.send_message("❌ La respuesta no puede estar vacía.", ephemeral=True)
            return

        if add_question(interaction.guild_id, pregunta, respuesta, dificultad.lower(), interaction.user.id):
            points = get_difficulty_points(dificultad.lower())
            await interaction.response.send_message(
                f"✅ Pregunta registrada.\n"
                f"**Dificultad:** {dificultad.lower()} ({points} pts)\n"
                f"**Q:** {pregunta}\n"
                f"**R:** ||{respuesta}||"
            )
        else:
            await interaction.response.send_message("❌ Error al registrar la pregunta. Inténtalo de nuevo.", ephemeral=True)

    @app_commands.command(name="trivia_del", description="[Admin] Elimina una pregunta por ID.")
    @app_commands.checks.has_permissions(administrator=True)
    async def trivia_del(self, interaction: discord.Interaction, question_id: int):
        if delete_question(question_id, interaction.guild_id):
            await interaction.response.send_message(f"🗑️ Pregunta `#{question_id}` eliminada.")
        else:
            await interaction.response.send_message(f"❌ No se encontró la pregunta `#{question_id}` en este servidor.", ephemeral=True)

    @app_commands.command(name="trivia_list", description="[Admin] Lista las últimas 10 preguntas registradas.")
    @app_commands.checks.has_permissions(administrator=True)
    async def trivia_list(self, interaction: discord.Interaction):
        questions = list_questions(interaction.guild_id)
        if not questions:
            await interaction.response.send_message("📭 No hay preguntas registradas en este servidor.", ephemeral=True)
            return

        lines = [f"`#{q['id']}` [{q['difficulty']}] {q['question']}" for q in questions]
        embed = discord.Embed(
            title="📋 Preguntas de Trivia",
            description="\n".join(lines),
            color=discord.Color.blue(),
        )
        embed.set_footer(text=f"Total: {get_question_count(interaction.guild_id)} preguntas")
        await interaction.response.send_message(embed=embed)

    # ── Comandos de juego ─────────────────────────────────────────────────────

    @app_commands.command(name="trivia", description="Inicia una pregunta de trivia.")
    async def trivia(self, interaction: discord.Interaction):
        if interaction.channel_id in _active_games:
            await interaction.response.send_message("⚠️ Ya hay una pregunta activa en este canal. ¡Respóndela primero!", ephemeral=True)
            return

        question = get_random_question(interaction.guild_id)
        if not question:
            await interaction.response.send_message(
                "📭 No hay preguntas registradas en este servidor.\n"
                "Contacta a un administrador para que agregue algunas.", ephemeral=True
            )
            return

        _active_games[interaction.channel_id] = question

        embed = discord.Embed(
            title="🎯 Trivia",
            description=question["question"],
            color=discord.Color.gold(),
        )
        embed.add_field(name="Dificultad", value=f"{question['difficulty']} (+{question['points']} pts)")
        embed.set_footer(text=f"Tienes {ANSWER_TIMEOUT} segundos para responder en el chat.")
        await interaction.response.send_message(embed=embed)

        def check(msg: discord.Message) -> bool:
            return (
                msg.channel.id == interaction.channel_id
                and not msg.author.bot
                and msg.content.lower().strip() == question["answer"].lower()
            )

        try:
            msg = await self.bot.wait_for("message", check=check, timeout=ANSWER_TIMEOUT)
            _active_games.pop(interaction.channel_id, None)

            add_points(interaction.guild_id, msg.author.id, question["points"])
            total = get_user_points(interaction.guild_id, msg.author.id)

            embed_win = discord.Embed(
                title="✅ ¡Correcto!",
                description=f"{msg.author.mention} acertó la respuesta: **{question['answer']}**",
                color=discord.Color.green(),
            )
            embed_win.add_field(name="Puntos ganados", value=f"+{question['points']} pts")
            embed_win.add_field(name="Puntos totales", value=f"{total} pts")
            await msg.channel.send(embed=embed_win)

        except asyncio.TimeoutError:
            _active_games.pop(interaction.channel_id, None)
            await interaction.channel.send(
                f"⏰ ¡Se acabó el tiempo! La respuesta era: **{question['answer']}**"
            )

    @app_commands.command(name="trivia_top", description="Muestra el ranking de puntos de trivia.")
    async def trivia_top(self, interaction: discord.Interaction):
        leaderboard = get_leaderboard(interaction.guild_id)
        if not leaderboard:
            await interaction.response.send_message("📭 Aún no hay puntos registrados en este servidor.")
            return

        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for i, row in enumerate(leaderboard):
            user = interaction.guild.get_member(row["user_id"])
            name = user.display_name if user else f"Usuario {row['user_id']}"
            prefix = medals[i] if i < 3 else f"`{i+1}.`"
            lines.append(f"{prefix} **{name}** — {row['points']} pts")

        embed = discord.Embed(
            title="🏆 Ranking de Trivia",
            description="\n".join(lines),
            color=discord.Color.gold(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="trivia_puntos", description="Muestra tus puntos de trivia en este servidor.")
    async def trivia_puntos(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        points = get_user_points(interaction.guild_id, target.id)
        await interaction.response.send_message(f"🎯 **{target.display_name}** tiene **{points} puntos** de trivia en este servidor.")

    @app_commands.command(name="trivia_dificultades", description="Muestra las dificultades disponibles y sus puntos.")
    async def trivia_dificultades(self, interaction: discord.Interaction):
        diffs = get_difficulties()
        if not diffs:
            await interaction.response.send_message("❌ No hay dificultades configuradas.")
            return
        lines = [f"**{d['name']}** → {d['points']} puntos" for d in diffs]
        embed = discord.Embed(
            title="📊 Dificultades de Trivia",
            description="\n".join(lines),
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Trivia(bot))
