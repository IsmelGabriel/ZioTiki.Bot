import json
import os

bot_status = {
    "status": "offline",
    "last_restart": None,
    "activity": "Helping users",
    "ping": "N/A",
}

STATUS_FILE = os.path.join(os.path.dirname(__file__), "..", "data", "bot_status.json")


def save_bot_status_json() -> None:
    """Persiste el estado actual del bot en data/bot_status.json."""
    try:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(bot_status, f)
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("No se pudo guardar bot_status.json: %s", e)


def load_bot_status_json() -> dict | None:
    """Lee data/bot_status.json y lo devuelve como dict, o None si no existe."""
    try:
        with open(STATUS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("No se pudo leer bot_status.json: %s", e)
        return None
