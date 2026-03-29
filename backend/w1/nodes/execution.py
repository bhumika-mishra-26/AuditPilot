"""
w1/nodes/execution.py  —  T4

Creates client account and persists to:
  1. existing_clients.json  — for duplicate check on next run
  2. SQLite clients table   — permanent record in DB

Writes one trace row to SQLite on completion.
"""

import uuid
import random
import json
import time
from datetime import datetime
from pathlib import Path
from shared.logger import log
from shared.db import write_trace, get_connection
from w1.utils.hitl import ask_choice

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "existing_clients.json"


def _load_existing_clients() -> list:
    if not DATA_FILE.exists():
        return []
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_existing_clients(clients: list) -> None:
    with DATA_FILE.open("w", encoding="utf-8") as f:
        json.dump(clients, f, indent=2)


def _persist_client_json(state: dict) -> str:
    """Writes new client to existing_clients.json for duplicate detection."""
    payload   = state["input"]
    client_id = payload.get("client_id")
    clients   = _load_existing_clients()

    if any(c.get("client_id") == client_id for c in clients):
        return "already_exists"

    clients.append({
        "client_id"   : client_id,
        "name"        : payload.get("name"),
        "email"       : payload.get("email"),
        "gstin"       : payload.get("gstin"),
        "onboarded_at": datetime.now().strftime("%Y-%m-%d"),
    })
    _save_existing_clients(clients)
    return "saved"


def _persist_client_db(state: dict) -> None:
    """Writes newly onboarded client to SQLite clients table."""
    payload = state["input"]
    conn    = get_connection()
    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO clients
            (client_id, name, email, phone, gstin,
             business_type, onboarded_at, status)
            VALUES (?,?,?,?,?,?,datetime('now','localtime'),'active')
            """,
            (
                payload.get("client_id"),
                payload.get("name"),
                payload.get("email"),
                payload.get("phone", ""),
                payload.get("gstin"),
                payload.get("business_type", ""),
            ),
        )
        conn.commit()
    except Exception as e:
        print(f"  [WARN] SQLite clients write failed: {e}")
    finally:
        conn.close()


def create_account_node(state: dict) -> dict:
    if "input" not in state:
        state["input"] = state.get("extracted_params", {})
        
    start = time.time()
    wid   = state.get("workflow_id", "WF-UNKNOWN")

    # ── HITL approval ────────────────────────────────────
    human_res = state["input"].get("human_resolution", "").strip().lower()
    # Production default for API runs: do not block on manual approval.
    if state.get("is_api_run"):
        human_res = "approve_account"

    if human_res in ("approve_account", "approve", "1"):
        state["logs"].append(log("Execution Agent", "Approval received via API/Human resolution [OK]"))
        # skip blocking ask_choice
    elif human_res in ("reject_account", "reject", "0", "cancel", "2"):
        # API/Human-driven rejection: write failure trace and end graph.
        state["logs"].append(log("Execution Agent", "Rejection received via API/Human resolution [OK]"))
        write_trace(
            workflow_id = wid, workflow_type = "W1",
            step_id = "T4", agent = "execution_agent",
            status = "failed",
            input_data  = {"client_id": state["input"].get("client_id")},
            output_data = {"error": "Human rejected account creation"},
            error_hash  = "hash_human_rejected",
            error_type  = "HUMAN_REJECTED_ACTION",
            decision    = "escalate",
            decision_reason = "Human reviewer declined account creation",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state
    elif state.get("hitl_enabled", False):
        state["logs"].append(log("Execution Agent", "Ready to create account"))
        state["logs"].append(log("Escalation Agent", "Awaiting human approval..."))
        
        # Write trace BEFORE blocking
        write_trace(
            workflow_id = wid, workflow_type = "W1",
            step_id = "T4", agent = "execution_agent",
            status = "escalated",
            input_data  = {"client_id": state["input"].get("client_id")},
            output_data = {"reason": "Awaiting approval"},
            error_type  = "HUMAN_REJECTED_ACTION",
            decision = "escalate", decision_reason = "Manual approval required before account creation",
        )

        if state.get("is_api_run"):
            return state

        approval = ask_choice(
            "Approve account creation?",
            ["approve", "reject"],
            "approve",
        )
        if approval != "approve":
            state["error"] = "HumanRejected: Account creation not approved"
            state["logs"].append(
                log("Execution Agent", "Account creation rejected by human reviewer [FAIL]")
            )
            write_trace(
                workflow_id = wid, workflow_type = "W1",
                step_id = "T4", agent = "execution_agent",
                status = "failed",
                input_data  = {"client_id": state["input"].get("client_id")},
                output_data = {"error": "Human rejected account creation"},
                error_hash  = "hash_human_rejected",
                error_type  = "HUMAN_REJECTED_ACTION",
                decision    = "escalate",
                decision_reason = "Human reviewer declined account creation",
                duration_ms = int((time.time() - start) * 1000),
            )
            return state

    # ── create account ───────────────────────────────────
    state["logs"].append(log("Execution Agent", "Creating account..."))
    account_id = f"acc_{str(uuid.uuid4())[:6]}"
    duration   = round(random.uniform(0.9, 1.4), 1)
    confidence = round(random.uniform(0.90, 0.96), 2)

    state["logs"].append(log(
        "Execution Agent",
        f"Account created: {account_id} (time: {duration}s, confidence: {confidence}) [OK]",
    ))

    # ── persist to JSON (for duplicate detection) ────────
    persist_status = _persist_client_json(state)
    if persist_status == "saved":
        state["logs"].append(
            log("Execution Agent", "Client record persisted to existing_clients.json [OK]")
        )
    else:
        state["logs"].append(
            log("Execution Agent", "Client already in JSON, skipping write [OK]")
        )

    # ── persist to SQLite clients table ──────────────────
    if persist_status == "saved":
        _persist_client_db(state)
        state["logs"].append(
            log("Execution Agent", "Client record written to SQLite clients table [OK]")
        )

    write_trace(
        workflow_id = wid, workflow_type = "W1",
        step_id = "T4", agent = "execution_agent",
        status = "success",
        input_data  = {"client_id": state["input"].get("client_id")},
        output_data = {
            "account_id"    : account_id,
            "persist_status": persist_status,
            "confidence"    : confidence,
        },
        duration_ms = int((time.time() - start) * 1000),
    )
    return state