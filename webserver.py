"""
Servidor de desarrollo — ejecutar directamente con:
    python webserver.py

Para producción usar wsgi.py con Gunicorn:
    gunicorn wsgi:app --bind 0.0.0.0:$PORT --workers 1
"""

from config import FLASK_HOST, FLASK_PORT, DEBUG
from bot import run_bot_thread
from web import create_app

run_bot_thread()

app = create_app()

if __name__ == "__main__":
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=DEBUG)
