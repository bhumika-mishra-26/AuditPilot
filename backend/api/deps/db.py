from shared.db import get_connection

def get_db():
    """
    FastAPI dependency that provides a SQLite connection.
    Ensures the connection is closed after the request.
    """
    db = get_connection()
    try:
        yield db
    finally:
        db.close()
