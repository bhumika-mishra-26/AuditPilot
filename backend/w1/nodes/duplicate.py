"""
w1/nodes/duplicate.py  —  T2

Checks if this client's email already exists
in existing_clients.json.
Writes one trace row to SQLite on completion.
"""

import json
import time
from pathlib import Path
from shared.logger import log
from shared.db import write_trace

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "existing_clients.json"


def _load_existing_clients() -> list:
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def duplicate_node(state: dict) -> dict:
    if "input" not in state:
        state["input"] = state.get("extracted_params", {})
        
    start = time.time()
    email = state["input"].get("email", "")
    wid   = state.get("workflow_id", "WF-UNKNOWN")

    state["logs"].append(log("Intake Agent", f"Checking duplicate for {email}"))

    existing = _load_existing_clients()
    duplicate = next(
        (c for c in existing if c.get("email") == email),
        None,
    )

    if duplicate:
        existing_name = duplicate.get("name", "existing client")
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