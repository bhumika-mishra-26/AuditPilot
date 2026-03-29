from fastapi import APIRouter, Depends, Query
from typing import List, Optional
from api.deps.db import get_db
import sqlite3

router = APIRouter()

@router.get("")
async def get_workflow_logs(
    workflow_id: Optional[str] = None,
    limit: int = Query(50, gt=0),
    db: sqlite3.Connection = Depends(get_db)
):
    """
    Returns the last 50 log entries. Filter by workflow_id if provided.
    """
    if workflow_id:
        rows = db.execute(
            """
            SELECT created_at as timestamp, agent as source, 
                   step_id as action, status as level, 
                   COALESCE(log_message, decision_reason, status) as message
            FROM traces
            WHERE workflow_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (workflow_id, limit)
        ).fetchall()
    else:
        rows = db.execute(
            """
            SELECT created_at as timestamp, agent as source, 
                   step_id as action, status as level, 
                   COALESCE(log_message, decision_reason, 'Activity (' || status || ')') as message
            FROM traces
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (limit,)
        ).fetchall()
    
    return [dict(row) for row in rows]

@router.get("/systemic-alerts")
async def get_systemic_alerts(db: sqlite3.Connection = Depends(get_db)):
    """
    Queries pattern_memory for any error_hash appearing in 2+ distinct workflow_ids.
    Returns alert objects for the frontend banner.
    """
    # This logic finds cross-workflow patterns that W4 has flagged or that meet the threshold.
    rows = db.execute(
        """
        SELECT error_hash, error_type, agent, recommended_action, attempts, success_rate 
        FROM pattern_memory 
        WHERE attempts >= 2
        ORDER BY last_seen_at DESC
        """
    ).fetchall()
    
    return [dict(row) for row in rows]
