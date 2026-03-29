"""
w1/nodes/kyc.py  —  T3

Calls mock KYC verification API.
C-005 fails on first attempt (simulates 503).
Writes one trace row to SQLite on completion.
"""

import time
from shared.logger import log
from shared.db import write_trace


def kyc_node(state: dict) -> dict:
    if "input" not in state:
        state["input"] = state.get("extracted_params", {})
    
    start = time.time()
    wid   = state.get("workflow_id", "WF-UNKNOWN")
    state["logs"].append(log("KYC Agent", "Calling KYC verification..."))

    # ── skip KYC if human approved override ─────────────
    if state.get("skip_kyc"):
        state["error"]      = None
        state["kyc_status"] = True
        state["logs"].append(log("KYC Agent", "KYC skipped by approved human override [OK]"))
        write_trace(
            workflow_id = wid, workflow_type = "W1",
            step_id = "T3", agent = "kyc_agent",
            status = "success",
            input_data  = {"skip_kyc": True},
            output_data = {"verified": True, "method": "human_override"},
            log_message = "KYC verified via human override",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    data      = state["input"]
    client_id = data.get("client_id")
    gstin     = data.get("gstin", "")

    # ── simulate 503 for C-005 on first attempt ──────────
    if client_id == "C-005" and state.get("retry_count", 0) == 0:
        state["error"]      = "KYC_503"
        state["kyc_status"] = False
        state["logs"].append(log("KYC Agent", "KYC API returned 503 [FAIL]"))
        write_trace(
            workflow_id = wid, workflow_type = "W1",
            step_id = "T3", agent = "kyc_agent",
            status = "failed",
            input_data  = {"client_id": client_id, "gstin": gstin, "attempt": state.get("retry_count", 0)},
            output_data = {"verified": False, "http_status": 503},
            error_hash  = "hash_503_kyc",
            error_type  = "HTTP_503_kyc_unavailable",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    # ── normal KYC check — GSTIN must be 15 chars or N/A ────────
    if len(gstin) == 15 or gstin == "N/A":
        state["error"]      = None
        state["kyc_status"] = True
        state["logs"].append(log("KYC Agent", "KYC verified successfully [OK]"))
        write_trace(
            workflow_id = wid, workflow_type = "W1",
            step_id = "T3", agent = "kyc_agent",
            status = "success",
            input_data  = {"client_id": client_id, "gstin": gstin},
            output_data = {"verified": True},
            log_message = "KYC verification successful",
            duration_ms = int((time.time() - start) * 1000),
        )
    else:
        state["error"]      = "Invalid GSTIN"
        state["kyc_status"] = False
        state["logs"].append(log("KYC Agent", "KYC invalid GSTIN length [FAIL]"))
        write_trace(
            workflow_id = wid, workflow_type = "W1",
            step_id = "T3", agent = "kyc_agent",
            status = "failed",
            input_data  = {"gstin": gstin},
            output_data = {"verified": False},
            error_hash  = "hash_gstin_val",
            error_type  = "GSTIN_format_invalid",
            duration_ms = int((time.time() - start) * 1000),
        )

    return state