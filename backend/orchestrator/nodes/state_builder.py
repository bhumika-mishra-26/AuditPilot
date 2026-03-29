"""
orchestrator/nodes/state_builder.py

Builds the initial state dict for each workflow
from the params extracted by the LLM classifier.

For W1 — builds W1State-compatible dict
For W2 — builds W2State-compatible dict
For W3 — builds W3State-compatible dict

For multi-task — builds a list of state dicts,
one per task, stored in state["built_states"].
"""

import uuid
import time
from shared.logger import log
from shared.db import write_trace


def _build_w1_state(params: dict, workflow_id: str) -> dict:
    """
    Builds initial W1 state from extracted params.
    Merges any params the LLM extracted into the input dict.
    The user or test data fills in missing fields.
    """
    return {
        "workflow_id"  : workflow_id,
        "input"        : {
            "client_id"    : params.get("client_id", f"C-{str(uuid.uuid4())[:4].upper()}"),
            "name"         : params.get("client_name", params.get("name", "")),
            "email"        : params.get("email", ""),
            "phone"        : params.get("phone", ""),
            "gstin"        : params.get("gstin", ""),
            "business_type": params.get("business_type", ""),
            # Used by API `/workflow/resume` to inject human-in-the-loop decisions.
            "human_resolution": params.get("human_resolution", ""),
        },
        "logs"         : [],
        "error"        : None,
        "retry_count"  : 0,
        "kyc_status"   : False,
        "hitl_enabled" : True,
        "skip_kyc"     : False,
        "w4_decision"  : None,
    }


def _build_w2_state(params: dict, workflow_id: str) -> dict:
    """
    Builds initial W2 state from extracted params.
    """
    def _safe_float(val):
        """Safely convert amount values to float, handling strings with commas."""
        if val is None: return 0.0
        if isinstance(val, (int, float)): return float(val)
        try:
            return float(str(val).replace(",", "").strip())
        except (ValueError, TypeError):
            return 0.0

    return {
        "workflow_id"  : workflow_id,
        "input"        : {
            "po_no"         : params.get("po_number", params.get("po_no", "")),
            "vendor_id"     : params.get("vendor_id", ""),
            "vendor_name"   : params.get("vendor_name", ""),
            "po_amount"     : _safe_float(params.get("amount", params.get("po_amount", 0))),
            "invoice_amount": _safe_float(params.get("invoice_amount", params.get("amount", 0))),
            "human_resolution": params.get("human_resolution", ""),
        },
        "logs"         : [],
        "error"        : None,
        "approved"     : False,
        "retry_count"  : 0,
        "status"       : "running",
        "w4_decision"  : None,
        "hitl_enabled" : True,
    }



def _build_w3_state(params: dict, workflow_id: str) -> dict:
    """
    Builds initial W3 state from extracted params.
    The 'notes' field is the raw meeting text.
    """
    return {
        "workflow_id"    : workflow_id,
        "notes"          : params.get("notes", params.get("meeting_notes", "")),
        "logs"           : [],
        "error"          : None,
        "status"         : "running",
        "tasks"          : [],
        "assigned_tasks" : [],
        "escalated_tasks": [],
        "human_required" : [],
        "tasks_written"  : 0,
        "w4_decision"    : None,
        "human_resolution": params.get("human_resolution", ""),
    }


BUILDERS = {
    "W1": _build_w1_state,
    "W2": _build_w2_state,
    "W3": _build_w3_state,
}


def state_builder_node(state: dict) -> dict:
    start     = time.time()
    task_list = state.get("task_list", [])

    if not task_list:
        # single task — use top-level route and params
        task_list = [{
            "route"           : state.get("route", "unclear"),
            "extracted_params": state.get("extracted_params", {}),
        }]

    built_states = []

    for task in task_list:
        route  = task.get("route", "unclear")
        params = task.get("extracted_params", {})

        # Inject global human_resolution into local params so sub-builders can use it
        hr = state.get("human_resolution")
        if hr:
            params["human_resolution"] = hr

        if route not in BUILDERS:
            state["logs"].append(
                log("Master Orchestrator", f"Unknown route '{route}' — skipping [WARN]")
            )
            continue

        # Use external workflow_id if provided (e.g. from API)
        wid = state.get("workflow_id")
        if not wid:
            wid = f"WF-{route}-{str(uuid.uuid4())[:6].upper()}"
        elif len(task_list) > 1:
            # Multi-task: add prefix/suffix to keep unique
            wid = f"WF-{route}-{wid[:8].upper()}"

        # Fallback for W3 if LLM failed to extract 'notes' specifically
        if route == "W3" and not params.get("notes") and not params.get("meeting_notes"):
            params["notes"] = state.get("user_task", "")

        built = BUILDERS[route](params, wid)
        from shared.logger import log
        state["logs"].append(log("State Builder", f"Building {route} state with params: {params}"))
        built["is_api_run"] = state.get("is_api_run", False)

        built_states.append({
            "route"       : route,
            "workflow_id" : wid,
            "state"       : built,
        })

        state["logs"].append(log(
            "Master Orchestrator",
            f"Built {route} state — workflow_id={wid} "
            f"params={list(params.keys())} [OK]"
        ))

        # log params for debugging resume flow
        state["logs"].append(log("Classifier", f"Classification finalized: route={route} params={list(params.keys())} [OK]"))
        write_trace(
            workflow_id   = state.get("workflow_id", "WF-UNKNOWN"),
            workflow_type = "ORCHESTRATOR",
            step_id       = "state_building",
            agent         = "master_orchestrator",
            status        = "success",
            input_data    = {"route": route, "params_count": len(params)},
            output_data   = {"workflow_id": wid},
            log_message   = f"Initialized {route} state for {wid}",
            duration_ms   = int((time.time() - start) * 1000),
        )

    state["built_states"] = built_states
    duration = int((time.time() - start) * 1000)
    state["logs"].append(log(
        "Master Orchestrator",
        f"State builder done — {len(built_states)} workflow(s) ready [{duration}ms]"
    ))

    return state