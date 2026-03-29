"""
w2/nodes/payment.py

Processes payment after approval.
Currently validates based on invoice vs PO amount match.

Real payment gateway integration is commented out below.
Uncomment the force_timeout block to demo W4 retry logic.
"""

import time
from shared.logger import log
from shared.db import write_trace


def payment_node(state: dict) -> dict:
    start = time.time()
    po    = state["input"]
    wid   = state.get("workflow_id", "WF-UNKNOWN")

    state["logs"].append(log("Payment Agent", "Processing payment..."))

    # skip if upstream error already set
    if state.get("error"):
        return state

    # ── DEMO: uncomment this block to simulate API_TIMEOUT
    #    and showcase W4 retry logic ──────────────────────
    # if state.get("retry_count", 0) == 0:
    #     state["error"] = "API_TIMEOUT"
    #     state["logs"].append(log("Payment Agent", "Payment API timed out [FAIL]"))
    #     write_trace(
    #         workflow_id = wid, workflow_type = "W2",
    #         step_id = "payment", agent = "payment_agent",
    #         status = "failed",
    #         input_data  = {"po_no": po.get("po_no"), "amount": po.get("po_amount")},
    #         output_data = {"error": "API timeout", "http_status": 408},
    #         error_hash  = "hash_408_timeout",
    #         error_type  = "HTTP_408_request_timeout",
    #         duration_ms = int((time.time() - start) * 1000),
    #     )
    #     return state
    # ────────────────────────────────────────────────────

    # ── current logic: validate payment based on
    #    invoice amount matching PO amount ────────────────
    po_amount      = po.get("po_amount", 0)
    invoice_amount = po.get("invoice_amount", 0)

    if po_amount <= 0:
        state["error"] = "THREE_WAY_MISMATCH"
        state["logs"].append(
            log("Payment Agent", "PO amount is zero — cannot process [FAIL]")
        )
        write_trace(
            workflow_id = wid, workflow_type = "W2",
            step_id = "payment", agent = "payment_agent",
            status = "failed",
            input_data  = {"po_no": po.get("po_no"), "po_amount": po_amount},
            output_data = {"error": "PO amount is zero"},
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    if invoice_amount != po_amount:
        diff = invoice_amount - po_amount
        state["error"] = "THREE_WAY_MISMATCH"
        state["logs"].append(
            log("Payment Agent",
                f"Payment blocked — invoice ₹{invoice_amount:,} "
                f"does not match PO ₹{po_amount:,} "
                f"(difference ₹{abs(diff):,}) [FAIL]")
        )
        write_trace(
            workflow_id = wid, workflow_type = "W2",
            step_id = "payment", agent = "payment_agent",
            status = "failed",
            input_data  = {"po_amount": po_amount, "invoice_amount": invoice_amount},
            output_data = {"error": "Amount mismatch", "difference": diff},
            error_hash  = "hash_invoice_mismatch",
            error_type  = "INVOICE_AMOUNT_MISMATCH",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    # ── amounts match — payment approved ─────────────────
    txn_ref = f"TXN-{int(time.time())}"
    state["status"] = "completed"
    state["logs"].append(
        log("Payment Agent",
            f"Payment validated — PO ₹{po_amount:,} matches invoice ₹{invoice_amount:,} [OK]")
    )
    state["logs"].append(
        log("Payment Agent", f"Payment approved — ref {txn_ref} [OK]")
    )
    write_trace(
        workflow_id = wid, workflow_type = "W2",
        step_id = "payment", agent = "payment_agent",
        status = "success",
        input_data  = {"po_no": po.get("po_no"), "amount": po_amount},
        output_data = {"txn_ref": txn_ref, "status": "completed"},
        duration_ms = int((time.time() - start) * 1000),
    )
    return state
