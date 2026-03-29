"""
w2/nodes/audit.py
Final audit log — records outcome and writes PO to SQLite.
Handles all statuses: completed, failed, pending_review.
"""

import time
from shared.logger import log
from shared.db import write_trace, get_connection


def audit_node(state: dict) -> dict:
    start  = time.time()
    wid    = state.get("workflow_id", "WF-UNKNOWN")
    status = state.get("status", "unknown")
    po     = state.get("input", {})

    state["logs"].append(log("Audit Agent", "Writing audit record..."))
    state["logs"].append(
        log("Audit Agent",
            f"Status: {status} | Retries: {state.get('retry_count', 0)} "
            f"| W4 decision: {state.get('w4_decision', 'none')} [OK]")
    )

    # ── write PO to SQLite purchase_orders table ──────────
    # runs for ALL outcomes — completed, failed, pending_review
    # so every PO processed is permanently recorded
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT OR REPLACE INTO purchase_orders
            (po_number, vendor_id, vendor_name, amount,
             invoice_amount, status, created_at)
            VALUES (?,?,?,?,?,?,datetime('now','localtime'))
            """,
            (
                po.get("po_no", wid),
                po.get("vendor_id", ""),
                po.get("vendor_name", ""),
                po.get("po_amount", 0),
                po.get("invoice_amount", 0),
                status,
            ),
        )
        conn.commit()
        state["logs"].append(
            log("Audit Agent",
                f"PO {po.get('po_no')} written to SQLite "
                f"with status={status} [OK]")
        )
    except Exception as e:
        state["logs"].append(
            log("Audit Agent", f"PO SQLite write failed: {e} [WARN]")
        )
    finally:
        conn.close()

    # ── write trace row ───────────────────────────────────
    write_trace(
        workflow_id = wid, workflow_type = "W2",
        step_id = "audit", agent = "audit_agent",
        status = "success",
        input_data  = {"status": status, "po_no": po.get("po_no")},
        output_data = {
            "final_status" : status,
            "retry_count"  : state.get("retry_count", 0),
            "w4_decision"  : state.get("w4_decision"),
            "approved"     : state.get("approved", False),
            "po_no"        : po.get("po_no"),
        },
        duration_ms = int((time.time() - start) * 1000),
    )
    return state
