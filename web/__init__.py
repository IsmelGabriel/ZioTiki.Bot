"""Paquete web — crea y configura la aplicación Flask."""

import logging
import os

from flask import Flask

from utils.db_schema import initialize_database
from web.routes import register_routes

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

    if not initialize_database():
        logger.error("No se pudo inicializar la base de datos al crear la app web.")

    # Registrar rutas y error handlers
    register_routes(app)

    logger.info("Flask app creada correctamente (debug=%s)", DEBUG)
    return app


__all__ = ["create_app"]
