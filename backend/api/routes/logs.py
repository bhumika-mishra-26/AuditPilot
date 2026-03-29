from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlmodel import Session, select, func
from api.deps.db import get_db
from shared.models import Trace, PatternMemory

router = APIRouter()

@router.get("")
async def get_workflow_logs(
    workflow_id: Optional[str] = None,
    limit: int = Query(50, gt=0),
    db: Session = Depends(get_db)
):
    """
    Returns the last 50 log entries. Filter by workflow_id if provided.
    """
    # We use a custom projection to match the frontend log format
    statement = select(
        Trace.created_at.label("timestamp"),
        Trace.agent.label("source"),
        Trace.step_id.label("action"),
        Trace.status.label("level"),
        func.coalesce(Trace.log_message, Trace.decision_reason, Trace.status).label("message")
    )
    
    if workflow_id:
        statement = statement.where(Trace.workflow_id == workflow_id)
        
    statement = statement.order_by(Trace.created_at.desc()).limit(limit)
    
    results = db.exec(statement).all()
    # results is a list of tuples since we selected specific columns
    return [
        {
            "timestamp": r[0],
            "source": r[1],
            "action": r[2],
            "level": r[3],
            "message": r[4]
        }
        for r in results
    ]

@router.get("/systemic-alerts")
async def get_systemic_alerts(db: Session = Depends(get_db)):
    """
    Queries pattern_memory for any error_hash appearing in 2+ distinct workflow_ids.
    Returns alert objects for the frontend banner.
    """
    statement = select(PatternMemory).where(PatternMemory.attempts >= 2).order_by(PatternMemory.last_seen_at.desc())
    results = db.exec(statement).all()
    return [r.model_dump() for r in results]
