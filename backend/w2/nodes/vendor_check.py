"""
w2/nodes/vendor_check.py
Looks up vendor in vendors.json.
Sets VENDOR_403 if inactive, VENDOR_404 if not found.
Writes trace row on completion.
"""

import json
import time
from pathlib import Path
from shared.logger import log
from shared.db import write_trace

DATA_FILE = Path(__file__).resolve().parent.parent.parent / "data" / "vendors.json"


def _load_vendors() -> list:
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)


def vendor_check_node(state: dict) -> dict:
    start     = time.time()
    state["error"] = None
    po        = state["input"]
    wid       = state.get("workflow_id", "WF-UNKNOWN")
    vendor_id = po.get("vendor_id")

    state["logs"].append(log("Vendor Agent", f"Looking up vendor {vendor_id}..."))

    vendors = _load_vendors()
    vendor  = next((v for v in vendors if v["vendor_id"] == vendor_id), None)

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
    if vendor.get("status") != "active":
        state["error"] = "VENDOR_403"
        state["logs"].append(
            log("Vendor Agent", f"Vendor {vendor_id} is inactive [FAIL]")
        )
        write_trace(
            workflow_id = wid, workflow_type = "W2",
            step_id = "vendor_check", agent = "vendor_agent",
            status = "failed",
            input_data  = {"vendor_id": vendor_id, "status": vendor.get("status")},
            output_data = {"found": True, "active": False, "http_status": 403},
            error_hash  = "hash_403_vendor",
            error_type  = "HTTP_403_vendor_inactive",
            duration_ms = int((time.time() - start) * 1000),
        )
        return state

    # ── vendor active ─────────────────────────────────────
    state["logs"].append(
        log("Vendor Agent", f"Vendor {vendor['name']} verified active [OK]")
    )
    write_trace(
        workflow_id = wid, workflow_type = "W2",
        step_id = "vendor_check", agent = "vendor_agent",
        status = "success",
        input_data  = {"vendor_id": vendor_id},
        output_data = {"found": True, "active": True, "name": vendor["name"]},
        duration_ms = int((time.time() - start) * 1000),
    )
    return state