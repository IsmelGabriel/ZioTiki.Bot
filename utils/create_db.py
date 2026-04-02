from utils.db_schema import initialize_database

def create_tables():
    """Compatibilidad: crea tablas usando el inicializador central."""
    return initialize_database(force=True)


# Solo ejecutar si se corre directamente
if __name__ == "__main__":
    create_tables()
