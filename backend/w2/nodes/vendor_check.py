"""
w2/nodes/vendor_check.py
Looks up vendor in the database (SQLModel/PostgreSQL).
Sets VENDOR_403 if inactive, VENDOR_404 if not found.
Writes trace row on completion.
"""

import time
from sqlmodel import Session, select
from shared.db import engine, write_trace
from shared.models import Vendor
from shared.logger import log


def vendor_check_node(state: dict) -> dict:
    start     = time.time()
    state["error"] = None
    po        = state["input"]
    wid       = state.get("workflow_id", "WF-UNKNOWN")
    vendor_id = po.get("vendor_id")

    state["logs"].append(log("Vendor Agent", f"Looking up vendor {vendor_id} in database..."))

    # ── Database Lookup ──────────────────────────────────
    with Session(engine) as session:
        statement = select(Vendor).where(Vendor.vendor_id == vendor_id)
        vendor = session.exec(statement).first()

    # ── vendor not found ─────────────────────────────────
    if not vendor:
        state["error"] = "VENDOR_404"
        state["logs"].append(
            log("Vendor Agent", f"Vendor {vendor_id} not found in system [FAIL]")
        )
        write_trace(
            workflow_id = wid, workflow_type = "W2",
            step_id = "vendor_check", agent = "vendor_agent",
            status = "failed",
            input_data  = {"vendor_id": vendor_id},
            output_data = {"found": False, "http_status": 404},
            error_hash  = "hash_404_vendor",
            error_type  = "HTTP_404_vendor_not_found",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    # ── vendor inactive ──────────────────────────────────
    if vendor.status != "active":
        state["error"] = "VENDOR_403"
        state["logs"].append(
            log("Vendor Agent", f"Vendor {vendor_id} is inactive [FAIL]")
        )
        write_trace(
            workflow_id = wid, workflow_type = "W2",
            step_id = "vendor_check", agent = "vendor_agent",
            status = "failed",
            input_data  = {"vendor_id": vendor_id, "status": vendor.status},
            output_data = {"found": True, "active": False, "http_status": 403},
            error_hash  = "hash_403_vendor",
            error_type  = "HTTP_403_vendor_inactive",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    # ── vendor active ─────────────────────────────────────
    state["logs"].append(
        log("Vendor Agent", f"Vendor {vendor.name} verified active [OK]")
    )
    write_trace(
        workflow_id = wid, workflow_type = "W2",
        step_id = "vendor_check", agent = "vendor_agent",
        status = "success",
        input_data  = {"vendor_id": vendor_id},
        output_data = {"found": True, "active": True, "name": vendor.name},
        duration_ms = int((time.time() - start) * 1000),
    )
    return state