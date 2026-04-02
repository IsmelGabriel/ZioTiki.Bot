"""Definición de rutas del dashboard web."""

import logging
from functools import wraps

from flask import render_template, jsonify, request, session, redirect, url_for

from config import DASHBOARD_PASSWORD
from utils.bot_status import bot_status
from web.services import get_error_logs, get_lasts_prompt_update

logger = logging.getLogger(__name__)


def login_required(f):
    """Decorator que protege rutas con autenticación por sesión."""
    @wraps(f)
    def decorated(*args, **kwargs):
        if not DASHBOARD_PASSWORD:
            return f(*args, **kwargs)
        if not session.get("authenticated"):
            return redirect(url_for("login"))
        return f(*args, **kwargs)
    return decorated


def register_routes(app):
    """Registra todas las rutas y error handlers en la app Flask."""

    # ── Autenticación ────────────────────────────────────────────────

    @app.route("/login", methods=["GET", "POST"])
    def login():
        if not DASHBOARD_PASSWORD:
            return redirect(url_for("home"))
        if request.method == "POST":
            if request.form.get("password") == DASHBOARD_PASSWORD:
                session["authenticated"] = True
                return redirect(url_for("home"))
            return render_template("login.html", error="Contraseña incorrecta."), 401
        return render_template("login.html")

    @app.route("/logout")
    def logout():
        session.pop("authenticated", None)
        return redirect(url_for("login"))

    # ── Páginas ──────────────────────────────────────────────────────

    @app.route("/")
    @login_required
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
    @login_required
    def api_ping():
        return jsonify({"ping": bot_status["ping"]})

    @app.route("/api/status")
    @login_required
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
