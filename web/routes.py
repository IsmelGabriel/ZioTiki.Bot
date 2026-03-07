"""Definición de rutas del dashboard web."""

import logging

from flask import render_template, jsonify

from utils.bot_status import bot_status
from web.services import get_error_logs, get_lasts_prompt_update

logger = logging.getLogger(__name__)


def register_routes(app):
    """Registra todas las rutas y error handlers en la app Flask."""

    # ── Páginas ──────────────────────────────────────────────────────

    @app.route("/")
    def home():
        error_logs = get_error_logs()
        prompts_update = get_lasts_prompt_update()
        return render_template(
            "home.html",
            bot_status=bot_status,
            error_logs=error_logs,
            prompts=prompts_update,
        )

    # ── API endpoints ────────────────────────────────────────────────

    @app.route("/api/ping")
    def api_ping():
        return jsonify({"ping": bot_status["ping"]})

    @app.route("/api/status")
    def api_status():
        """Endpoint para obtener todo el estado del bot."""
        return jsonify(bot_status)

    # ── Error handlers ───────────────────────────────────────────────

    @app.errorhandler(404)
    def not_found(error):
        return jsonify({"error": "Not found"}), 404

    @app.errorhandler(500)
    def internal_error(error):
        logger.error("Error interno del servidor: %s", error)
        return jsonify({"error": "Internal server error"}), 500
