"""
Punto de entrada para producción (Gunicorn / Render / Railway).

Uso:
    gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1

NOTA: Se usa 1 worker porque el bot de Discord corre en un hilo
dentro del mismo proceso. Con múltiples workers se duplicaría el bot.
"""

from bot import run_bot_thread
from web import create_app

# Iniciar el bot de Discord en un hilo aparte
run_bot_thread()

# Crear la app Flask (Gunicorn busca esta variable)
app = create_app()
