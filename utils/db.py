import logging

import psycopg2
from psycopg2 import pool
from psycopg2.extras import RealDictCursor
from typing import Optional, Tuple, Any

from config import DB_CONFIG

logger = logging.getLogger(__name__)

_pool: Optional[pool.ThreadedConnectionPool] = None


def _get_pool() -> pool.ThreadedConnectionPool:
    """Initializes (once) and returns the connection pool."""
    global _pool
    if _pool is None or _pool.closed:
        try:
            _pool = pool.ThreadedConnectionPool(minconn=1, maxconn=10, **DB_CONFIG)
        except Exception as e:
            logger.error("No se pudo crear el pool de conexiones: %s", e)
            raise
    return _pool


def conectar():
    """Obtiene una conexión del pool."""
    try:
        return _get_pool().getconn()
    except Exception as e:
        logger.error("No se pudo obtener conexión del pool: %s", e)
        return None


def liberar(conn):
    """Devuelve una conexión al pool."""
    try:
        _get_pool().putconn(conn)
    except Exception:
        pass


# Alias para compatibilidad interna
_release = liberar


def execute_query(query: str, params: Optional[Tuple[Any, ...]] = None):
    """Ejecuta una consulta (INSERT, UPDATE, DELETE) con commit automático."""
    conn = conectar()
    if not conn:
        return False
    try:
        with conn:
            with conn.cursor() as cur:
                cur.execute(query, params)
        return True
    except Exception as e:
        logger.error("Error ejecutando query: %s", e)
        return False
    finally:
        _release(conn)


def fetch_query(query: str, params: Optional[Tuple[Any, ...]] = None):
    """Ejecuta una consulta SELECT y devuelve los resultados."""
    conn = conectar()
    if not conn:
        return None
    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(query, params)
                return cur.fetchall()
    except Exception as e:
        logger.error("Error en SELECT: %s", e)
        return None
    finally:
        _release(conn)
