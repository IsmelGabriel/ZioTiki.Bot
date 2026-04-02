from utils.db import execute_query, fetch_query  # Importamos las funciones del módulo db

def save_message(server_id: int, user_id: int, role: str, content: str):
    """Guarda un mensaje en la base de datos."""
    query = """
        INSERT INTO memories (server_id, user_id, role, content)
        VALUES (%s, %s, %s, %s)
    """
    params = (server_id, user_id, role, content)
    execute_query(query, params)


def get_history(server_id: int, user_id: int):
    """Obtiene el historial de conversación de un usuario en un servidor."""
    query = """
        SELECT role, content
        FROM memories
        WHERE server_id = %s AND user_id = %s
        ORDER BY id ASC
        LIMIT 15
    """
    params = (server_id, user_id)
    return fetch_query(query, params) or []


def clear_history(server_id: int, user_id: int):
    """Limpia la memoria de un usuario en un servidor."""
    query = "DELETE FROM memories WHERE server_id = %s AND user_id = %s"
    params = (server_id, user_id)
    execute_query(query, params)
