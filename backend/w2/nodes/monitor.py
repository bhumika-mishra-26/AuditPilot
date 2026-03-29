"""
w2/nodes/monitor.py
Detects errors after payment attempt.
Writes trace row on completion.
"""

import time
from shared.logger import log
from shared.db import write_trace


def monitor_node(state: dict) -> dict:
    start = time.time()
    wid   = state.get("workflow_id", "WF-UNKNOWN")

    if state.get("error"):
        state["logs"].append(
            log("Monitor Agent", f"Error detected: {state['error']}")
        )
    else:
        state["logs"].append(log("Monitor Agent", "All steps completed — no errors [OK]"))

    write_trace(
        workflow_id = wid, workflow_type = "W2",
        step_id = "monitor", agent = "monitor_agent",
        status = "failed" if state.get("error") else "success",
        input_data  = {"error": state.get("error")},
        output_data = {"has_error": bool(state.get("error"))},
        duration_ms = int((time.time() - start) * 1000),
    )
    return state