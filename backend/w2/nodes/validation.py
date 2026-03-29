"""
w2/nodes/validation.py
Three-way match — checks invoice amount vs PO amount.
Writes trace row on completion.
"""

import time
from shared.logger import log
from shared.db import write_trace


def validation_node(state: dict) -> dict:
    start = time.time()
    state["error"] = None
    po    = state["input"]
    wid   = state.get("workflow_id", "WF-UNKNOWN")

    state["logs"].append(log("Validation Agent", "Checking invoice match..."))

    po_amount      = po.get("po_amount", 0)
    invoice_amount = po.get("invoice_amount", 0)

    if invoice_amount != po_amount:
        diff = invoice_amount - po_amount
        state["error"] = "THREE_WAY_MISMATCH"
        state["logs"].append(
            log("Validation Agent", f"Mismatch detected: invoice higher by ₹{diff} [FAIL]")
        )
        write_trace(
            workflow_id = wid, workflow_type = "W2",
            step_id = "validation", agent = "validation_agent",
            status = "failed",
            input_data  = {"po_amount": po_amount, "invoice_amount": invoice_amount},
            output_data = {"match": False, "discrepancy": diff},
            error_hash  = "hash_invoice_mismatch",
            error_type  = "INVOICE_AMOUNT_MISMATCH",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    state["logs"].append(log("Validation Agent", "Invoice amount matches PO [OK]"))
    write_trace(
        workflow_id = wid, workflow_type = "W2",
        step_id = "validation", agent = "validation_agent",
        status = "success",
        input_data  = {"po_amount": po_amount, "invoice_amount": invoice_amount},
        output_data = {"match": True},
        duration_ms = int((time.time() - start) * 1000),
    )
    return state