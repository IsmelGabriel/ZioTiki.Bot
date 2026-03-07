"""
Configuración centralizada del proyecto.
Usa variables de entorno (.env) para datos sensibles.
"""

import os
from dotenv import load_dotenv

load_dotenv()


# ── Entorno ─────────────────────────────────────────────────────────
ENV = os.getenv("FLASK_ENV", "production")  # "development" | "production"
DEBUG = ENV == "development"

# ── Discord ─────────────────────────────────────────────────────────
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
TESTING_MODE = os.getenv("TESTING_MODE", "False").lower() == "true"

# ── Base de datos (PostgreSQL) ──────────────────────────────────────
DB_CONFIG = {
    "dbname": os.getenv("dbname"),
    "user": os.getenv("user"),
    "password": os.getenv("password"),
    "host": os.getenv("host"),
    "port": int(os.getenv("port", 5432)),
}

# ── OpenAI ──────────────────────────────────────────────────────────
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

# ── Flask ───────────────────────────────────────────────────────────
SECRET_KEY = os.getenv("SECRET_KEY", os.urandom(32).hex())
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
