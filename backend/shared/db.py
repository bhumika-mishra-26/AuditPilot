"""
shared/db.py

Single SQLite connection used by every agent.
W1, W2, W3, W4, and master orchestrator all import from here.

Usage:
    from shared.db import get_connection

    conn = get_connection()
    conn.execute("SELECT * FROM traces")
    conn.close()
"""

import sqlite3
import os
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "auditpilot.db"


def get_connection() -> sqlite3.Connection:
    """
    Returns a SQLite connection with:
    - Row factory set so columns can be accessed by name (row["error_hash"])
    - WAL mode for safe concurrent reads and writes
    - Foreign keys enforced
    - check_same_thread=False for async/multithreaded environments
    """
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False, timeout=10)
    conn.row_factory = sqlite3.Row
    
    # Consistent PRAGMAs for AuditPilot
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA cache_size=-64000") # 64MB cache
    return conn


def write_trace(
    workflow_id:    str,
    workflow_type:  str,
    step_id:        str,
    agent:          str,
    status:         str,
    input_data:     dict = None,
    output_data:    dict = None,
    error_hash:     str  = None,
    error_type:     str  = None,
    decision:       str  = None,
    decision_reason:str  = None,
    log_message:    str  = None,
    duration_ms:    int  = None,
):
    """
    Writes one row to the traces table.

    Called by every agent node after it completes —
    whether success or failure.

    Parameters
    ----------
    workflow_id     : unique ID for this run e.g. "WF-C005"
    workflow_type   : "W1" | "W2" | "W3" | "W4"
    step_id         : node name e.g. "T1", "T3", "validate", "kyc"
    agent           : agent name e.g. "validation_agent", "kyc_agent"
    status          : "success" | "failed" | "escalated" | "retried"
    input_data      : dict of what the node received (will be JSON-serialised)
    output_data     : dict of what the node produced (will be JSON-serialised)
    error_hash      : W4 hash e.g. "hash_503_kyc" — None if no error
    error_type      : W4 error type string — None if no error
    decision        : what was decided e.g. "retry" | "escalate" — None if no error
    decision_reason : plain-English reason for the decision
    log_message     : detailed activity message for frontend
    duration_ms     : how long the step took in milliseconds
    """
    import json

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO traces
            (workflow_id, workflow_type, step_id, agent,
             input_data, output_data, status,
             error_hash, error_type, decision, decision_reason,
             log_message, duration_ms, created_at)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,datetime('now','localtime'))
            """,
            (
                workflow_id,
                workflow_type,
                step_id,
                agent,
                json.dumps(input_data)  if input_data  else None,
                json.dumps(output_data) if output_data else None,
                status,
                error_hash,
                error_type,
                decision,
                decision_reason,
                log_message,
                duration_ms,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def read_pattern(error_hash: str) -> dict | None:
    """
    Reads one row from pattern_memory for the given error_hash.
    Returns a plain dict or None if not found.

    Used by W4 T14 to get the recommended action and success rate.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT * FROM pattern_memory WHERE error_hash = ?",
            (error_hash,),
        ).fetchone()
        if row is None:
            return None
        return dict(row)
    finally:
        conn.close()


def update_pattern(error_hash: str, retry_succeeded: bool):
    """
    Updates attempts and success_rate in pattern_memory.
    Called by W4 T16 after every resolution.

    If the error_hash does not exist yet, does nothing.
    New patterns are inserted by W4 agent.py separately.
    """
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT attempts, successes FROM pattern_memory WHERE error_hash = ?",
            (error_hash,),
        ).fetchone()

        if row is None:
            return

        new_attempts  = row["attempts"]  + 1
        new_successes = row["successes"] + (1 if retry_succeeded else 0)
        new_rate      = new_successes / new_attempts

        conn.execute(
            """
            UPDATE pattern_memory
            SET attempts = ?,
                successes = ?,
                success_rate = ?,
                last_seen_at = datetime('now','localtime')
            WHERE error_hash = ?
            """,
            (new_attempts, new_successes, new_rate, error_hash),
        )
        conn.commit()
    finally:
        conn.close()


def count_affected_workflows(error_hash: str) -> tuple[int, list[str]]:
    """
    Counts how many distinct workflow_ids have this error_hash
    in the traces table with status failed or escalated.

    Returns (count, [workflow_id, ...])
    Used by W4 T13 for cross-workflow detection.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            """
            SELECT DISTINCT workflow_id
            FROM traces
            WHERE error_hash = ?
            AND status IN ('failed', 'escalated')
            """,
            (error_hash,),
        ).fetchall()
        affected = [row["workflow_id"] for row in rows]
        return len(affected), affected
    finally:
        conn.close()


def write_systemic_alert(
    error_hash:         str,
    error_type:         str,
    affected_workflows: list[str],
    context:            str = None,
):
    """
    Inserts one row into systemic_alerts table.
    Called by W4 T15 when count >= 3 workflows.
    """
    import json

    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT INTO systemic_alerts
            (error_hash, error_type, affected_workflows,
             occurrence_count, context, created_at)
            VALUES (?,?,?,?,?,datetime('now','localtime'))
            """,
            (
                error_hash,
                error_type,
                json.dumps(affected_workflows),
                len(affected_workflows),
                context,
            ),
        )
        conn.commit()
    finally:
        conn.close()


def get_workflow_tasks(workflow_id: str) -> list[dict]:
    """
    Returns all tasks (assigned and escalated) for a specific workflow.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE workflow_id = ? ORDER BY created_at ASC",
            (workflow_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_systemic_alerts() -> list[dict]:
    """
    Returns all unresolved systemic alerts.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM systemic_alerts WHERE resolved = 0 ORDER BY created_at DESC"
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_briefing_history(limit: int = 10) -> list[dict]:
    """
    Returns recent generated briefings from the briefing_log.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM briefing_log ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_all_traces(limit: int = 100) -> list[dict]:
    """
    Returns the most recent traces across all workflows.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM traces ORDER BY created_at DESC LIMIT ?",
            (limit,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def get_workflow_traces(workflow_id: str) -> list[dict]:
    """
    Returns all traces for a specific workflow_id.
    """
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM traces WHERE workflow_id = ? ORDER BY created_at ASC",
            (workflow_id,),
        ).fetchall()
        return [dict(row) for row in rows]
    finally:
        conn.close()


def update_workflow_input(workflow_id: str, input_payload: dict):
    """
    Updates the input_payload for a specific workflow_id in the workflows table.
    Used to persist human corrections (e.g. GSTIN) so they survive restarts.
    """
    import json
    conn = get_connection()
    try:
        conn.execute(
            "UPDATE workflows SET input_payload = ? WHERE workflow_id = ?",
            (json.dumps(input_payload), workflow_id)
        )
        conn.commit()
    finally:
        conn.close()