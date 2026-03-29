"""
w2/nodes/intake.py
Logs the PO being processed. Writes trace row.
"""

import time
from shared.logger import log
from shared.db import write_trace


def intake_node(state: dict) -> dict:
    start = time.time()
    state["error"] = None
    po    = state["input"]
    wid   = state.get("workflow_id", "WF-UNKNOWN")

    state["logs"].append(log("Intake Agent", f"Processing {po.get('po_no')}"))

    write_trace(
        workflow_id = wid, workflow_type = "W2",
        step_id = "intake", agent = "intake_agent",
        status = "success",
        input_data  = {"po_no": po.get("po_no"), "vendor_id": po.get("vendor_id")},
        output_data = {"received": True},
        duration_ms = int((time.time() - start) * 1000),
    )
    return state