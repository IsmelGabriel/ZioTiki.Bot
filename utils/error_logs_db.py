from datetime import datetime
from utils.db import conectar, liberar
import traceback

def log_error(error_message, server_id=None, user_id=None, error_type="Unknown", stack_trace=None):
    """
    Registra un error detallado en la base de datos.

    Args:
        error_message (str): Mensaje de error descriptivo
        server_id (int): ID del servidor donde ocurrió el error
        user_id (int): ID del usuario que causó el error (opcional)
        error_type (str): Tipo de error (CommandError, DatabaseError, etc.)
        stack_trace (str): Stack trace completo del error (opcional)

    Returns:
        bool: True si se guardó exitosamente, False en caso contrario
    """
    conn = conectar()
    if not conn:
        print("[ERROR] No se pudo conectar a la base de datos para registrar el error.")
        return

    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    try:
        with conn.cursor() as cur:
            # Verificar si la tabla tiene la columna stack_trace
            query = """
                INSERT INTO error_logs (server_id, user_id, error_type, error_message, stack_trace, created_at)
                VALUES (%s, %s, %s, %s, %s, %s);
            """
            params = (server_id, user_id, error_type, error_message, stack_trace, fecha_hora)

            cur.execute(query, params)
            conn.commit()
            print(f"[ERROR LOG] {error_type} registrado para server {server_id or 'global'} - Usuario: {user_id or 'N/A'}")
            return True
    except Exception as e:
        print(f"[ERROR] No se pudo registrar el error en BD: {e}")
        # Si la tabla no tiene todas las columnas, intentar con campos básicos
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO error_logs (server_id, error_message, created_at)
                    VALUES (%s, %s, NOW())
                    """,
                    (server_id, f"{error_type}: {error_message}"),
                )
                conn.commit()
                return True
        except Exception as e2:
            print(f"[ERROR] Intento fallido de registro alternativo: {e2}")
            return False
    finally:
        liberar(conn)


def log_command_error(ctx, error):
    """
    Registra errores de comandos de Discord.

    Args:
        ctx: El contexto del comando
        error: La excepción del error
    """
    server_id = ctx.guild.id if ctx.guild else None
    user_id = ctx.author.id
    error_type = type(error).__name__
    error_message = str(error)
    stack_trace = traceback.format_exc()

    log_error(
        error_message=error_message,
        server_id=server_id,
        user_id=user_id,
        error_type=error_type,
        stack_trace=stack_trace
    )


def log_database_error(error_message, server_id=None, user_id=None):
    """Registra errores de base de datos."""
    log_error(
        error_message=error_message,
        server_id=server_id,
        user_id=user_id,
        error_type="DatabaseError",
        stack_trace=traceback.format_exc()
    )


def log_ai_error(error_message, server_id=None, user_id=None):
    """Registra errores de IA/OpenAI."""
    log_error(
        error_message=error_message,
        server_id=server_id,
        user_id=user_id,
        error_type="AIError",
        stack_trace=traceback.format_exc()
    )
