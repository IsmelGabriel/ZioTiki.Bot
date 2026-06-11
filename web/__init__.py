"""Paquete web — crea y configura la aplicación Flask."""

import logging
import os

from flask import Flask

from utils.db_schema import initialize_database
from web.routes import register_routes
from flask_cors import CORS

logger = logging.getLogger(__name__)


def create_app():
    """
    Application factory para Flask.

    Configura:
    - SECRET_KEY para sesiones seguras
    - Carpeta de templates relativa al paquete
    - Logging de errores en producción
    - Registro de rutas
    """
    from config import SECRET_KEY, DEBUG

    template_dir = os.path.join(os.path.dirname(__file__), "templates")
    static_dir = os.path.join(os.path.dirname(__file__), "static")

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir,
    )

    app.config["SECRET_KEY"] = SECRET_KEY
    app.config["DEBUG"] = DEBUG

    # Configurar CORS permitiendo el portal en producción y local
    CORS(app, origins=[
        "https://mi-portal-z8nr.onrender.com",
        "https://discord-bot-rh78.onrender.com"
        "http://127.0.0.1:5001",
        "http://localhost:5001",
        "http://192.168.0.12:5001"
    ])

    if not initialize_database():
        logger.error("No se pudo inicializar la base de datos al crear la app web.")

    # Registrar rutas y error handlers
    register_routes(app)

    logger.info("Flask app creada correctamente (debug=%s)", DEBUG)
    return app


__all__ = ["create_app"]
