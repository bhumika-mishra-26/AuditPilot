"""
w2/nodes/approval.py
Auto-approves POs above ₹1,00,000.
Writes trace row on completion.
"""

import time
from shared.logger import log
from shared.db import write_trace


def approval_node(state: dict) -> dict:
    start    = time.time()
    state["error"] = None
    po       = state["input"]
    wid   = state.get("workflow_id", "WF-UNKNOWN")
    amount = po.get("po_amount", 0)

    if amount > 100000:
        state["approved"] = True
        state["logs"].append(
            log("Approval Agent", f"PO ₹{amount:,} — approval required and auto-approved [OK]")
        )
    else:
        state["logs"].append(
            log("Approval Agent", f"PO ₹{amount:,} — below threshold, no approval needed [OK]")
        )

    write_trace(
        workflow_id = wid, workflow_type = "W2",
        step_id = "approval", agent = "approval_agent",
        status = "success",
        input_data  = {"po_amount": amount},
        output_data = {"approved": state.get("approved", False), "threshold": 100000},
        duration_ms = int((time.time() - start) * 1000),
    )
    return state