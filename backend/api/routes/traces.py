from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from sqlmodel import Session, select
from api.deps.db import get_db
from shared.models import Trace

router = APIRouter()

@router.get("")
async def get_traces(
    workflow_id: Optional[str] = None,
    outcome: Optional[str] = None,
    limit: int = Query(100, gt=0),
    db: Session = Depends(get_db)
):
    """
    Returns full trace rows for a workflow_id with optional outcome filter.
    Used by the trace explorer.
    """
    statement = select(Trace)
    
    if workflow_id:
        statement = statement.where(Trace.workflow_id == workflow_id)
        
    if outcome:
        statement = statement.where(Trace.status == outcome)
        
    statement = statement.order_by(Trace.created_at.desc()).limit(limit)
    
    results = db.exec(statement).all()
    return [r.model_dump() for r in results]
