"""
w1/nodes/validation.py  —  T1

Validates incoming client data.
Checks name, email format, and GSTIN length.
Writes one trace row to SQLite on completion.
"""

import time
from shared.logger import log
from shared.db import write_trace, update_workflow_input
from shared.error_map import get_error_hash
from w1.utils.hitl import ask_choice, ask_text
import os


def validate_node(state: dict) -> dict:
    if "input" not in state:
        state["input"] = state.get("extracted_params", {})
    
    start = time.time()
    state["logs"].append(log("Validation Agent", "Running schema validation..."))

    data  = state["input"]
    email = data.get("email", "")
    name  = data.get("name")
    gstin = state["input"].get("gstin", "")
    wid   = state.get("workflow_id", "WF-UNKNOWN")
    human_res = state["input"].get("human_resolution", "").strip()

    state["logs"].append(log("Validation Agent", f"NODE START: gstin='{gstin}', human_res='{human_res}'"))
    # ── name check ──────────────────────────────────────
    if not isinstance(name, str) or not name.strip():
        state["error"] = "Missing Name"
        state["logs"].append(log("Validation Agent", "Missing name field [FAIL]"))
        
        err_hash, err_type = get_error_hash(state["error"])
        write_trace(
            workflow_id = wid, workflow_type = "W1",
            step_id = "T1", agent = "validation_agent",
            status = "escalated",
            input_data  = {"name": name, "email": email, "gstin": gstin},
            output_data = {"error": "Missing name"},
            error_hash  = err_hash, error_type = err_type,
            decision = "escalate", decision_reason = "Name missing — data problem",
            log_message = "Name missing — escalation required",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    # ── email check ─────────────────────────────────────
    if not isinstance(email, str) or not email.strip() or "@" not in email:
        state["error"] = "Missing Email"
        state["logs"].append(log("Validation Agent", "Missing or invalid email [FAIL]"))
        
        err_hash, err_type = get_error_hash(state["error"])
        write_trace(
            workflow_id = wid, workflow_type = "W1",
            step_id = "T1", agent = "validation_agent",
            status = "escalated",
            input_data  = {"email": email},
            output_data = {"error": "Invalid email"},
            error_hash  = err_hash, error_type = err_type,
            decision = "escalate", decision_reason = "Email missing or invalid — data problem",
            log_message = "Email missing or invalid — escalation required",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    # ── GSTIN check ─────────────────────────────────────
    # Prioritize resolution from API/Human
    human_res = state["input"].get("human_resolution", "").strip()
    
    # Is the CURRENT gstin still invalid?
    current_gstin_invalid = not isinstance(gstin, str) or len(gstin.strip()) != 15
    
    # If the user provides a direct correction (15 chars)
    if len(human_res) == 15 and current_gstin_invalid:
        gstin = human_res
        state["input"]["gstin"] = gstin
        state["logs"].append(log("Validation Agent", f"Using human-provided correction: {gstin} [OK]"))
        # Persist the correction back to the workflows table
        state["logs"].append(log("Validation Agent", f"Persisting updated payload to DB for {wid}..."))
        update_workflow_input(wid, state["input"])
        current_gstin_invalid = False
    
    # If the user opts to skip the GSTIN requirement
    elif human_res == "skip_gstin" and current_gstin_invalid:
        gstin = "N/A"
        state["input"]["gstin"] = "N/A"
        state["logs"].append(log("Validation Agent", "Human opted to skip GSTIN requirement [OK]"))
        update_workflow_input(wid, state["input"])
        current_gstin_invalid = False
    
    # If the user just chose "correct" but ONLY if the GSTIN is still invalid!
    elif human_res == "correct" and current_gstin_invalid:
        state["logs"].append(log("Validation Agent", "User chose to correct GSTIN. Awaiting 15-character value..."))
        state["error"] = 'ValidationError: "Please type the 15-char GSTIN in the box"'
        # Re-escalate with this specific error so the API can show it
        err_hash, err_type = get_error_hash(state["error"])
        write_trace(
            workflow_id = wid, workflow_type = "W1",
            step_id = "T1", agent = "validation_agent",
            status = "escalated",
            input_data  = {"previous_action": "1"},
            output_data = {"reason": "Awaiting text entry"},
            error_hash  = err_hash, error_type = "GSTIN_format_invalid",
            decision = "escalate", decision_reason = "Please enter the new GSTIN below.",
        )
        return state

    if current_gstin_invalid:
        state["error"] = 'ValidationError: "GSTIN must be 15 characters"'
        state["logs"].append(
            log("Validation Agent", 'ValidationError: "GSTIN must be 15 characters" [FAIL]')
        )

        if state.get("hitl_enabled", False):
            state["logs"].append(
                log("Escalation Agent", "Human action required: Correct GSTIN or cancel")
            )
            # Write trace BEFORE blocking
            err_hash, err_type = get_error_hash(state["error"])
            write_trace(
                workflow_id = wid, workflow_type = "W1",
                step_id = "T1", agent = "validation_agent",
                status = "escalated",
                input_data  = {"gstin": gstin},
                output_data = {"reason": "GSTIN length invalid"},
                error_hash  = err_hash, error_type = err_type,
                decision = "escalate", decision_reason = "GSTIN must be 15 characters",
            )
            
            if state.get("is_api_run") or os.environ.get("API_MODE") == "1":
                return state
            
            choice = ask_choice(
                "Validation failed. Choose action",
                ["correct", "cancel"],
                "cancel",
            )
            if choice == "correct":
                new_gstin = ask_text("Enter corrected GSTIN (15 chars)", gstin).strip()
                if len(new_gstin) == 15:
                    state["input"]["gstin"] = new_gstin
                    state["error"] = None
                    state["logs"].append(
                        log("Validation Agent", "GSTIN corrected by human review [OK]")
                    )
                    # Update trace to success
                    write_trace(
                        workflow_id = wid, workflow_type = "W1",
                        step_id = "T1", agent = "validation_agent",
                        status = "success",
                        input_data  = {"gstin_original": gstin, "gstin_corrected": new_gstin},
                        output_data = {"validated": True},
                        log_message = "All fields validated successfully",
                        duration_ms = int((time.time() - start) * 1000),
                    )
                    return state
                else:
                    state["logs"].append(
                        log("Validation Agent", "Corrected GSTIN still invalid [FAIL]")
                    )

        err_hash, err_type = get_error_hash(state["error"])
        write_trace(
            workflow_id = wid, workflow_type = "W1",
            step_id = "T1", agent = "validation_agent",
            status = "failed",
            input_data  = {"gstin": gstin, "length": len(gstin)},
            output_data = {"error": "GSTIN must be 15 characters"},
            error_hash  = err_hash,
            error_type  = err_type,
            decision    = "escalate",
            decision_reason = "Format errors are data problems — retry never helps",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    # ── all passed ──────────────────────────────────────
    state["logs"].append(log("Validation Agent", "All fields validated successfully [OK]"))
    write_trace(
        workflow_id = wid, workflow_type = "W1",
        step_id = "T1", agent = "validation_agent",
        status = "success",
        input_data  = {"name": name, "email": email, "gstin": gstin},
        output_data = {"validated": True},
        log_message = "All fields validated successfully",
        duration_ms = int((time.time() - start) * 1000),
    )
    return state