"""
w3/nodes/error.py

W3 error node — W4 integration point.
Called whenever intake or extraction fails.
Owner resolution calls W4 directly per task,
so this node handles workflow-level failures only.
"""

import time
from shared.logger import log
from shared.db import write_trace
from shared.error_map import get_error_hash, is_retryable
from w4.agent import run_w4


def error_node(state: dict) -> dict:
    start     = time.time()
    error_str = state.get("error", "")
    wid       = state.get("workflow_id", "WF-UNKNOWN")

    state["logs"].append(log("Monitor Agent", f"Error detected: {error_str}"))

    error_hash, error_type = get_error_hash(error_str)

    write_trace(
        workflow_id = wid, workflow_type = "W3",
        step_id = "error_node", agent = "monitor_agent",
        status = "escalated",
        input_data  = {"error": error_str},
        output_data = {"calling_w4": True, "error_hash": error_hash},
        error_hash  = error_hash,
        error_type  = error_type,
        log_message = f"Error '{error_str}' triggers W4 analysis",
        duration_ms = int((time.time() - start) * 1000),
    )

    # intake errors are always data problems — skip W4
    if not is_retryable(error_hash):
        state["logs"].append(
            log("Monitor Agent", "Non-retryable error — escalating [FAIL]")
        )
        state["w4_decision"] = "escalate"
        state["status"]      = "failed"
        return state

    # call W4 for retryable errors (api_timeout, api_error)
    state["logs"].append(
        log("Monitor Agent", f"Calling W4 for {error_hash}...")
    )

    w4_result = run_w4(
        workflow_id    = wid,
        workflow_type  = "W3",
        error_hash     = error_hash,
        error_type     = error_type,
        retry_succeeded= False,
    )

    decision = w4_result["decision"]["decision"]
    rate     = w4_result["decision"].get("success_rate")

    state["w4_decision"] = decision
    state["logs"].append(log(
        "Explainability Agent",
        f"W4 decision: {decision.upper()} (rate={rate})"
    ))

    if decision == "escalate":
        state["status"] = "failed"

    return state