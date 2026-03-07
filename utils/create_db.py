from config import DB_CONFIG
import psycopg2

def create_tables():
    """Crea las tablas necesarias en la base de datos si no existen."""
    commands = [
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
            )
        """,
        """
            CREATE TABLE IF NOT EXISTS memories (
                id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                server_id BIGINT NOT NULL,
                user_id BIGINT NOT NULL,
                role TEXT NOT NULL,
                content TEXT NOT NULL
            )
        """,
        """
            CREATE TABLE IF NOT EXISTS error_logs (
                id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                server_id BIGINT,
                user_id BIGINT,
                error_type VARCHAR(100) NOT NULL,
                error_message TEXT NOT NULL,
                stack_trace TEXT,
                create_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """,
        """
            CREATE TABLE IF NOT EXISTS prompts (
                id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
                server_id BIGINT,
                name VARCHAR(100) NOT NULL,
                content TEXT NOT NULL,
                updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE (server_id, name)
            )
        """
    ]

    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        for command in commands:
            cur.execute(command)
        conn.commit()
        cur.close()
        conn.close()
        print("Tablas creadas exitosamente o ya existían.")
    except Exception as e:
        print(f"[ERROR] No se pudieron crear las tablas: {e}")


# Solo ejecutar si se corre directamente
if __name__ == "__main__":
    create_tables()
