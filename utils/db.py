import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import closing

from config import DB_CONFIG

def conectar():
    """Conecta a la base de datos y devuelve la conexión."""
    try:
        return psycopg2.connect(**DB_CONFIG)
    except Exception as e:
        print(f"[ERROR] No se pudo conectar a la base de datos: {e}")
        return None


def execute_query(query: str, params: tuple = None):
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
        print(f"[ERROR] Error ejecutando query: {e}")
        return False
    finally:
        conn.close()


def fetch_query(query: str, params: tuple = None):
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
        print(f"[ERROR] Error en SELECT: {e}")
        return None
    finally:
        conn.close()
