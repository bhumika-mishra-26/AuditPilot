"""
w3/nodes/intake.py

Validates that meeting notes are not empty
and at least 15 words long.
Writes trace row to SQLite on completion.
"""

import time
from shared.logger import log, log_step
from shared.db import write_trace


def intake_node(state: dict) -> dict:
    start  = time.time()
    state["error"] = None
    wid    = state.get("workflow_id", "WF-UNKNOWN")
    notes  = state.get("notes", "")

    state["logs"].append(log("Intake Agent", "Validating meeting notes..."))
    
    # ── HITL Correction ──────────────────────────────────
    hr = state.get("human_resolution")
    if hr and hr.lower() not in ["1", "1 (continue)", "retry", "resume", "cancel"]:
        # Only treat this as note correction if the original notes were genuinely broken
        # AND it's not a known dashboard button command or short name (len < 4 words)
        if len(notes.strip().split()) < 15 and len(hr.strip().split()) >= 3:
            state["notes"] = hr
            state["logs"].append(log("Intake Agent", "Received corrected notes from human [OK]"))
    
    notes  = state.get("notes", "")
    # ── empty check ──────────────────────────────────────
    if not notes or notes.strip() == "":
        state["error"]  = "intake_error"
        state["status"] = "failed"
        state["logs"].append(log("Intake Agent", "Notes are empty [FAIL]"))
        write_trace(
            workflow_id = wid, workflow_type = "W3",
            step_id = "T9_intake", agent = "intake_agent",
            status = "failed",
            input_data  = {"word_count": 0},
            output_data = {"error": "Notes are empty"},
            error_hash  = "hash_intake_empty",
            error_type  = "INTAKE_NOTES_INVALID",
            decision    = "escalate",
            decision_reason = "Empty notes — data problem",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    word_count = len(notes.strip().split())

    # ── too short check ──────────────────────────────────
    if word_count < 15:
        state["error"]  = "intake_error"
        state["status"] = "failed"
        state["logs"].append(
            log("Intake Agent", f"Notes too short — {word_count} words [FAIL]")
        )
        write_trace(
            workflow_id = wid, workflow_type = "W3",
            step_id = "T9_intake", agent = "intake_agent",
            status = "failed",
            input_data  = {"word_count": word_count},
            output_data = {"error": f"Too short: {word_count} words, minimum 15"},
            error_hash  = "hash_intake_empty",
            error_type  = "INTAKE_NOTES_INVALID",
            decision    = "escalate",
            decision_reason = f"Notes too short ({word_count} words) — data problem",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    # ── passed ───────────────────────────────────────────
    state["logs"].append(
        log("Intake Agent", f"{word_count} words — validation passed [OK]")
    )
    write_trace(
        workflow_id = wid, workflow_type = "W3",
        step_id = "T9_intake", agent = "intake_agent",
        status = "success",
        input_data  = {"word_count": word_count},
        output_data = {"validated": True},
        log_message = f"Validation passed ({word_count} words)",
        duration_ms = int((time.time() - start) * 1000),
    )
    return state