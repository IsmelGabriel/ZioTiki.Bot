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

    # ── Admin commands ────────────────────────────────────────────────────────
    @app_commands.command(name="trivia_add", description="[Admin] Add a trivia question. d: easy/medium/hard")
    @app_commands.checks.has_permissions(administrator=True)
    async def trivia_add(self, interaction: discord.Interaction, difficulty: str, question: str, answer: str):
        diff_map = {"easy": "facil", "medium": "medio", "hard": "dificil"}
        diff_key = diff_map.get(difficulty.lower(), difficulty.lower())

        if get_difficulty_points(diff_key) is None:
            diffs = ", ".join(f"`{d['name']}`" for d in get_difficulties())
            await interaction.response.send_message(f"❌ Difficulty `{difficulty}` does not exist. Options: {diffs}", ephemeral=True)
            return

        if len(question) < 5:
            await interaction.response.send_message("❌ The question is too short.", ephemeral=True)
            return

        if len(answer) < 1:
            await interaction.response.send_message("❌ The answer cannot be empty.", ephemeral=True)
            return

        if add_question(interaction.guild_id, question, answer, diff_key, interaction.user.id):
            points = get_difficulty_points(diff_key)
            await interaction.response.send_message(
                f"✅ Question registered.\n"
                f"**Difficulty:** {difficulty.lower()} ({points} pts)\n"
                f"**Q:** {question}\n"
                f"**A:** ||{answer}||"
            )
        else:
            await interaction.response.send_message("❌ Error registering the question. Please try again.", ephemeral=True)

    @app_commands.command(name="trivia_del", description="[Admin] Delete a question by ID.")
    @app_commands.checks.has_permissions(administrator=True)
    async def trivia_del(self, interaction: discord.Interaction, question_id: int):
        if delete_question(question_id, interaction.guild_id):
            await interaction.response.send_message(f"🗑️ Question `#{question_id}` deleted.")
        else:
            await interaction.response.send_message(f"❌ Question `#{question_id}` was not found in this server.", ephemeral=True)

    @app_commands.command(name="trivia_list", description="[Admin] List the last 10 registered questions.")
    @app_commands.checks.has_permissions(administrator=True)
    async def trivia_list(self, interaction: discord.Interaction):
        questions = list_questions(interaction.guild_id)
        if not questions:
            await interaction.response.send_message("📭 There are no questions registered in this server.", ephemeral=True)
            return

        lines = [f"`#{q['id']}` [{q['difficulty']}] {q['question']}" for q in questions]
        embed = discord.Embed(
            title="📋 Trivia Questions",
            description="\n".join(lines),
            color=discord.Color.blue(),
        )
        embed.set_footer(text=f"Total: {get_question_count(interaction.guild_id)} questions")
        await interaction.response.send_message(embed=embed)

    # ── Game commands ─────────────────────────────────────────────────────────

    @app_commands.command(name="trivia", description="Start a trivia question.")
    async def trivia(self, interaction: discord.Interaction):
        if interaction.channel_id in _active_games:
            await interaction.response.send_message("⚠️ There is already an active question in this channel. Answer it first!", ephemeral=True)
            return

        question = get_random_question(interaction.guild_id)
        if not question:
            await interaction.response.send_message(
                "📭 There are no questions registered in this server.\n"
                "Contact an administrator to add some.", ephemeral=True
            )
            return

        _active_games[interaction.channel_id] = question

        embed = discord.Embed(
            title="🎯 Trivia",
            description=question["question"],
            color=discord.Color.gold(),
        )
        embed.add_field(name="Difficulty", value=f"{question['difficulty']} (+{question['points']} pts)")
        embed.set_footer(text=f"You have {ANSWER_TIMEOUT} seconds to answer in chat.")
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
                title="✅ Correct!",
                description=f"{msg.author.mention} guessed the answer: **{question['answer']}**",
                color=discord.Color.green(),
            )
            embed_win.add_field(name="Points earned", value=f"+{question['points']} pts")
            embed_win.add_field(name="Total points", value=f"{total} pts")
            await msg.channel.send(embed=embed_win)

        except asyncio.TimeoutError:
            _active_games.pop(interaction.channel_id, None)
            await interaction.channel.send(
                f"⏰ Time's up! The answer was: **{question['answer']}**"
            )

    @app_commands.command(name="trivia_top", description="Show the trivia leaderboard.")
    async def trivia_top(self, interaction: discord.Interaction):
        leaderboard = get_leaderboard(interaction.guild_id)
        if not leaderboard:
            await interaction.response.send_message("📭 No points registered in this server yet.")
            return

        medals = ["🥇", "🥈", "🥉"]
        lines = []
        for i, row in enumerate(leaderboard):
            user = interaction.guild.get_member(row["user_id"])
            name = user.display_name if user else f"User {row['user_id']}"
            prefix = medals[i] if i < 3 else f"`{i+1}.`"
            lines.append(f"{prefix} **{name}** — {row['points']} pts")

        embed = discord.Embed(
            title="🏆 Trivia Leaderboard",
            description="\n".join(lines),
            color=discord.Color.gold(),
        )
        await interaction.response.send_message(embed=embed)

    @app_commands.command(name="trivia_points", description="Show your trivia points in this server.")
    async def trivia_points(self, interaction: discord.Interaction, member: discord.Member = None):
        target = member or interaction.user
        points = get_user_points(interaction.guild_id, target.id)
        await interaction.response.send_message(f"🎯 **{target.display_name}** has **{points} trivia points** in this server.")

    @app_commands.command(name="trivia_difficulties", description="Show available difficulties and their points.")
    async def trivia_difficulties(self, interaction: discord.Interaction):
        diffs = get_difficulties()
        if not diffs:
            await interaction.response.send_message("❌ No difficulties configured.")
            return
        lines = [f"**{d['name']}** → {d['points']} points" for d in diffs]
        embed = discord.Embed(
            title="📊 Trivia Difficulties",
            description="\n".join(lines),
            color=discord.Color.blurple(),
        )
        await interaction.response.send_message(embed=embed)

async def setup(bot):
    await bot.add_cog(Trivia(bot))
