from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from api.deps.db import get_db
import sqlite3

router = APIRouter()

@router.get("")
async def get_traces(
    workflow_id: Optional[str] = None,
    outcome: Optional[str] = None,
    limit: int = Query(100, gt=0),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Returns full trace rows for a workflow_id with optional outcome filter.
    Used by the trace explorer.
    """
    query = "SELECT * FROM traces"
    params = []
    
    conditions = []
    if workflow_id:
        conditions.append("workflow_id = ?")
        params.append(workflow_id)
        
    if outcome:
        conditions.append("status = ?")
        params.append(outcome)
        
    if conditions:
        query += " WHERE " + " AND ".join(conditions)
        
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(limit)
    
    rows = db.execute(query, params).fetchall()
    return [dict(row) for row in rows]
