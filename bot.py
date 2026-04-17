import os
import threading
from datetime import datetime
import logging
import discord
import asyncio
from discord.ext import commands, tasks

from config import DISCORD_TOKEN, TESTING_MODE
from utils.logger_db import guardar_log
from utils.ia import generate_response
from utils.error_logs_db import log_command_error, log_ai_error
from utils.bot_status import bot_status, save_bot_status_json
from utils.db_schema import initialize_database

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


intents = discord.Intents.default()
intents.message_content = True
intents.members = True  # Enable member intents

bot = commands.Bot(command_prefix="=", intents=intents, help_command=None)

@bot.event
async def on_ready():
    logger.info(f"Bot is online: '{bot.user}'")
    logger.info(f"Bot ID: '{bot.user.id}'")
    bot_status["status"] = "Online"
    bot_status["last_restart"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    bot_status["ping"] = round(bot.latency * 1000)
    save_bot_status_json()

    server_count = len(bot.guilds)
    logger.info(f"Connected to {server_count} servers.")

    # List servers
    for guild in bot.guilds:
        logger.info(f" - {guild.name} (ID: {guild.id})")

    # Iniciar tarea de actualización de ping
    if not update_ping.is_running():
        update_ping.start()

@tasks.loop(minutes=1)
async def update_ping():
    """Actualiza el ping del bot cada 1 minuto."""
    bot_status["ping"] = round(bot.latency * 1000)
    save_bot_status_json()


@bot.event
async def on_command_error(ctx, error):
    logger.error(f"Command error: '{ctx.command}': {str(error)}")
    # Registrar el error en la base de datos
    log_command_error(ctx, error)

@bot.event
async def on_message(message):
    if message.author.bot:
        return

    if not message.guild:
        return

    guardar_log(
        level="INFO",
        server_id=message.guild.id if message.guild else 0,
        author_id=message.author.id,
        author_name=str(message.author),
        mensaje=message.content
    )

    if bot.user in message.mentions and not message.mention_everyone:
        prompt = message.content.replace(f"<@{bot.user.id}>", "").replace(f"<@!{bot.user.id}>", "").strip()
        if not prompt:
            await message.channel.send("👋 Hello! How can I assist you today?")

        elif len(prompt) > 300:
            await message.channel.send("⚠️ Your message is too long! Please keep it under 300 characters.")

        else:
            async with message.channel.typing():
                server_id = message.guild.id if message.guild else 0
                try:
                    response = await asyncio.to_thread(
                        generate_response, server_id, message.author.id, prompt
                    )
                    user = message.author.mention
                    await message.channel.send(response + f"\n{user}")
                except Exception as e:
                    log_ai_error(
                        error_message=str(e),
                        server_id=server_id,
                        user_id=message.author.id
                    )
                    await message.channel.send(
                        "El sistema de IA no esta disponible en este "
                        "momento o se encuentra en mantenimiento!"
                    )

    await bot.process_commands(message)


async def load_cogs():
    # Verify cogs directory exists
    cogs_dir = "./cogs"
    if not os.path.exists(cogs_dir):
        logger.error(f"Directory '{cogs_dir}' not found!")
        return

    for filename in os.listdir(cogs_dir):
        if filename.endswith(".py"):
            try:
                await bot.load_extension(f"cogs.{filename[:-3]}")
                logger.info(f"Loaded extension: {filename}")
            except Exception as e:
                logger.error(f"Failed to load extension {filename}: {str(e)}")

_bot_started = False

def start_bot():
    global _bot_started
    if _bot_started:
        logger.warning("Bot is already running!")
        return

    if not initialize_database():
        logger.error("Database initialization failed. Bot startup aborted.")
        return

    if TESTING_MODE:
        logger.info("Bot is running in TESTING MODE.")
        async def test_runner():
            async with bot:
                await load_cogs()
                if not DISCORD_TOKEN:
                    logger.error("No Discord token found!")
                    return
                await bot.start(DISCORD_TOKEN)
        asyncio.run(test_runner())
        return
    async def runner():
        async with bot:
            await load_cogs()
            if not DISCORD_TOKEN:
                logger.error("No Discord token found!")
                return
            await bot.start(DISCORD_TOKEN)

    asyncio.run(runner())

def run_bot_thread():
    thread = threading.Thread(target=start_bot, daemon=True)
    thread.start()


if __name__ == "__main__":
    start_bot()
