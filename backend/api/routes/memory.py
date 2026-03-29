from fastapi import APIRouter, Depends
from api.deps.db import get_db
import sqlite3

router = APIRouter()

@router.get("")
async def get_pattern_memory(db: sqlite3.Connection = Depends(get_db)):
    """
    Returns all rows from pattern_memory table ordered by last_seen descending.
    Used by the memory panel.
    """
    rows = db.execute("SELECT * FROM pattern_memory ORDER BY last_seen_at DESC").fetchall()
    return [dict(row) for row in rows]
