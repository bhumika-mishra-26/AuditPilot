"""
w1/nodes/duplicate.py  —  T2

Checks if this client's email already exists
in the database (SQLModel/PostgreSQL).
Writes one trace row to SQLite on completion.
"""

import time
from sqlmodel import Session, select
from shared.db import engine, write_trace
from shared.models import Client
from shared.logger import log


def duplicate_node(state: dict) -> dict:
    if "input" not in state:
        state["input"] = state.get("extracted_params", {})
        
    start = time.time()
    email = state["input"].get("email", "")
    wid   = state.get("workflow_id", "WF-UNKNOWN")

    state["logs"].append(log("Intake Agent", f"Checking duplicate for {email}"))

    # ── Database Lookup ──────────────────────────────────
    with Session(engine) as session:
        statement = select(Client).where(Client.email == email)
        duplicate = session.exec(statement).first()

    if duplicate:
        existing_name = duplicate.name
        state["error"] = f'DuplicateError: "Email already registered under {existing_name}"'
        state["logs"].append(
            log("Intake Agent", f"Duplicate found for {existing_name} [FAIL]")
        )
        write_trace(
            workflow_id = wid, workflow_type = "W1",
            step_id = "T2", agent = "intake_agent",
            status = "failed",
            input_data  = {"email": email},
            output_data = {"is_duplicate": True, "existing_name": existing_name},
            error_hash  = "hash_duplicate",
            error_type  = "DUPLICATE_CLIENT",
            decision    = "escalate",
            decision_reason = "Duplicate emails are always data problems",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    state["logs"].append(log("Intake Agent", "No duplicate found [OK]"))
    write_trace(
        workflow_id = wid, workflow_type = "W1",
        step_id = "T2", agent = "intake_agent",
        status = "success",
        input_data  = {"email": email},
        output_data = {"is_duplicate": False},
        duration_ms = int((time.time() - start) * 1000),
    )
    return state