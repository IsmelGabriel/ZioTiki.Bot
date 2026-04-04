"""Servicios de consulta a base de datos para el dashboard web."""

from psycopg2.extras import RealDictCursor
from utils.db import conectar, liberar


def get_error_logs():
    """Obtiene los últimos 10 errores registrados con más detalles."""
    conn = conectar()
    if not conn:
        return []

    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    """
                    SELECT
                        server_id,
                        user_id,
                        error_type,
                        error_message,
                        created_at,
                        CASE WHEN stack_trace IS NOT NULL THEN TRUE ELSE FALSE END as has_stack_trace
                    FROM error_logs
                    ORDER BY created_at DESC
                    LIMIT 10;
                    """
                )
                logs = cur.fetchall()
                return logs if logs else []
    except Exception as e:
        print(f"[ERROR] No se pudieron obtener los logs de error: {e}")
        try:
            with conn:
                with conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute(
                        "SELECT server_id, error_message, created_at FROM error_logs ORDER BY created_at DESC LIMIT 10;"
                    )
                    logs = cur.fetchall()
                    return logs if logs else []
        except Exception as e2:
            print(f"[ERROR] Fallback también falló: {e2}")
            return []
    finally:
        liberar(conn)


def get_lasts_prompt_update():
    """Obtiene las últimas 5 actualizaciones de prompts."""
    conn = conectar()
    if not conn:
        return []

    try:
        with conn:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute(
                    "SELECT server_id, name, content, updated_at FROM prompts ORDER BY updated_at DESC LIMIT 5;"
                )
                prompts = cur.fetchall()
                return prompts if prompts else []
    except Exception as e:
        print(f"[ERROR] No se pudo obtener la última actualización de prompt: {e}")
        return []
    finally:
        liberar(conn)
