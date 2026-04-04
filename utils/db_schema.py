"""Esquema de base de datos y utilidades de inicializacion."""

import threading

import psycopg2

from config import DB_CONFIG

SCHEMA_STATEMENTS = [
    """
    CREATE TABLE IF NOT EXISTS logs (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        level VARCHAR(10) NOT NULL,
        server_id BIGINT NOT NULL,
        author_id BIGINT,
        author_name VARCHAR(100),
        message TEXT NOT NULL,
        content_type VARCHAR(50),
        timestamp TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS memories (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        server_id BIGINT NOT NULL,
        user_id BIGINT NOT NULL,
        role TEXT NOT NULL,
        content TEXT NOT NULL
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS error_logs (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        server_id BIGINT,
        user_id BIGINT,
        error_type VARCHAR(100) NOT NULL,
        error_message TEXT NOT NULL,
        stack_trace TEXT,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS prompts (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        server_id BIGINT,
        name VARCHAR(100) NOT NULL,
        content TEXT NOT NULL,
        updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
        UNIQUE (server_id, name)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_memories_server_user_id
    ON memories (server_id, user_id, id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_error_logs_created_at
    ON error_logs (created_at DESC);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_prompts_server_name
    ON prompts (server_id, name);
    """,
    # ── Trivia ──────────────────────────────────────────────────────
    """
    CREATE TABLE IF NOT EXISTS trivia_difficulties (
        id SMALLINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        name VARCHAR(50) NOT NULL UNIQUE,
        points SMALLINT NOT NULL
    );
    """,
    """
    INSERT INTO trivia_difficulties (name, points)
    VALUES ('facil', 1), ('medio', 3), ('dificil', 5)
    ON CONFLICT (name) DO NOTHING;
    """,
    """
    CREATE TABLE IF NOT EXISTS trivia_questions (
        id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
        server_id BIGINT NOT NULL,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        difficulty VARCHAR(50) NOT NULL REFERENCES trivia_difficulties(name),
        created_by BIGINT NOT NULL,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    );
    """,
    """
    CREATE TABLE IF NOT EXISTS trivia_scores (
        server_id BIGINT NOT NULL,
        user_id BIGINT NOT NULL,
        points BIGINT NOT NULL DEFAULT 0,
        PRIMARY KEY (server_id, user_id)
    );
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_trivia_questions_server
    ON trivia_questions (server_id);
    """,
    """
    CREATE INDEX IF NOT EXISTS idx_trivia_scores_server_points
    ON trivia_scores (server_id, points DESC);
    """,
]

_db_init_lock = threading.Lock()
_db_initialized = False


def initialize_database(force: bool = False) -> bool:
    """Crea o actualiza el esquema minimo requerido por la aplicacion."""
    global _db_initialized

    if _db_initialized and not force:
        return True

    with _db_init_lock:
        if _db_initialized and not force:
            return True

        try:
            with psycopg2.connect(**DB_CONFIG) as conn:
                with conn.cursor() as cur:
                    for statement in SCHEMA_STATEMENTS:
                        cur.execute(statement)

                # Compatibilidad con instalaciones antiguas (create_at -> created_at)
                with conn.cursor() as cur:
                    cur.execute(
                        """
                        ALTER TABLE error_logs
                        ADD COLUMN IF NOT EXISTS created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP;
                        """
                    )
            _db_initialized = True
            print("[DB] Esquema verificado correctamente.")
            return True
        except Exception as e:
            print(f"[ERROR] No se pudo inicializar la base de datos: {e}")
            return False
