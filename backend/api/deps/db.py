from sqlmodel import Session
from shared.db import engine

def get_db():
    """
    FastAPI dependency that provides a SQLModel session.
    Ensures the session is closed after the request.
    """
    with Session(engine) as session:
        yield session
