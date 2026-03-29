from fastapi import APIRouter, Depends
from sqlmodel import Session, select
from api.deps.db import get_db
from shared.models import PatternMemory

router = APIRouter()

@router.get("")
async def get_pattern_memory(db: Session = Depends(get_db)):
    """
    Returns all rows from pattern_memory table ordered by last_seen descending.
    Used by the memory panel.
    """
    statement = select(PatternMemory).order_by(PatternMemory.last_seen_at.desc())
    results = db.exec(statement).all()
    return [r.model_dump() for r in results]
