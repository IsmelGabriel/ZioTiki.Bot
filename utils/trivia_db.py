"""Operaciones de base de datos para el sistema de trivia."""

import logging
from typing import Optional

from utils.db import execute_query, fetch_query

logger = logging.getLogger(__name__)


# ── Dificultades ─────────────────────────────────────────────────────────────

def get_difficulties() -> list:
    """Devuelve todas las dificultades con sus puntos."""
    return fetch_query("SELECT name, points FROM trivia_difficulties ORDER BY points ASC") or []


def get_difficulty_points(difficulty: str) -> Optional[int]:
    """Devuelve los puntos de una dificultad, o None si no existe."""
    rows = fetch_query(
        "SELECT points FROM trivia_difficulties WHERE name = %s",
        (difficulty.lower(),),
    )
    return rows[0]["points"] if rows else None


# ── Preguntas ─────────────────────────────────────────────────────────────────

def add_question(server_id: int, question: str, answer: str, difficulty: str, created_by: int) -> bool:
    """Guarda una nueva pregunta de trivia."""
    return execute_query(
        """
        INSERT INTO trivia_questions (server_id, question, answer, difficulty, created_by)
        VALUES (%s, %s, %s, %s, %s)
        """,
        (server_id, question, answer.lower().strip(), difficulty.lower(), created_by),
    )


def get_random_question(server_id: int) -> Optional[dict]:
    """Obtiene una pregunta aleatoria del servidor."""
    rows = fetch_query(
        """
        SELECT q.id, q.question, q.answer, q.difficulty, d.points
        FROM trivia_questions q
        JOIN trivia_difficulties d ON d.name = q.difficulty
        WHERE q.server_id = %s
        ORDER BY RANDOM()
        LIMIT 1
        """,
        (server_id,),
    )
    return rows[0] if rows else None


def get_question_count(server_id: int) -> int:
    """Devuelve el número total de preguntas del servidor."""
    rows = fetch_query(
        "SELECT COUNT(*) AS total FROM trivia_questions WHERE server_id = %s",
        (server_id,),
    )
    return rows[0]["total"] if rows else 0


def delete_question(question_id: int, server_id: int) -> bool:
    """Elimina una pregunta por ID (solo del servidor indicado)."""
    return execute_query(
        "DELETE FROM trivia_questions WHERE id = %s AND server_id = %s",
        (question_id, server_id),
    )


def list_questions(server_id: int, limit: int = 10) -> list:
    """Devuelve las últimas preguntas registradas en el servidor."""
    return fetch_query(
        """
        SELECT id, question, difficulty
        FROM trivia_questions
        WHERE server_id = %s
        ORDER BY created_at DESC
        LIMIT %s
        """,
        (server_id, limit),
    ) or []


# ── Puntuaciones ─────────────────────────────────────────────────────────────

def add_points(server_id: int, user_id: int, points: int) -> bool:
    """Suma puntos al usuario en el servidor. Crea la fila si no existe."""
    return execute_query(
        """
        INSERT INTO trivia_scores (server_id, user_id, points)
        VALUES (%s, %s, %s)
        ON CONFLICT (server_id, user_id) DO UPDATE
            SET points = trivia_scores.points + EXCLUDED.points
        """,
        (server_id, user_id, points),
    )


def get_user_points(server_id: int, user_id: int) -> int:
    """Devuelve los puntos de un usuario en el servidor."""
    rows = fetch_query(
        "SELECT points FROM trivia_scores WHERE server_id = %s AND user_id = %s",
        (server_id, user_id),
    )
    return rows[0]["points"] if rows else 0


def get_leaderboard(server_id: int, limit: int = 10) -> list:
    """Devuelve el top de usuarios con más puntos en el servidor."""
    return fetch_query(
        """
        SELECT user_id, points
        FROM trivia_scores
        WHERE server_id = %s
        ORDER BY points DESC
        LIMIT %s
        """,
        (server_id, limit),
    ) or []
