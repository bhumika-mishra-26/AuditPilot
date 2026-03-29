"""
orchestrator/nodes/invoke_workflows.py

Invokes W1, W2, or W3 graphs based on built_states.

Single task  → invokes one graph synchronously
Multi-task   → invokes multiple graphs using
               ThreadPoolExecutor for parallel execution

All three workflows use graph.invoke(state) now
since W3 was rebuilt as LangGraph in Phase 5.
"""

import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from shared.logger import log
from shared.db import write_trace


def _invoke_one(route: str, workflow_id: str, wf_state: dict) -> dict:
    """
    Invokes a single workflow graph and returns the result.
    Imports are done inside this function so each thread
    gets a clean import without circular dependency issues.
    """
    if route == "W1":
        from w1.graph import graph
    elif route == "W2":
        from w2.graph import graph
    elif route == "W3":
        from w3.graph import graph
    else:
        return {
            "route"      : route,
            "workflow_id": workflow_id,
            "status"     : "error",
            "error"      : f"Unknown route: {route}",
            "logs"       : [],
        }

    try:
        result = graph.invoke(wf_state)
        # Determine final status robustly across workflows.
        #
        # W1 typically uses `error` to indicate failure.
        # W2/W3 may clear `error` after escalation and instead rely on `status`
        # (e.g., "failed", "completed", "pending_review"), so using `error` alone
        # incorrectly reports success.
        final_status = result.get("status")
        w4_decision = result.get("w4_decision")
        
        if final_status == "completed":
            status = "success"
        elif final_status in ("pending_review", "escalated"):
            status = "escalated"
        elif final_status == "failed":
            status = "failed"
        elif w4_decision == "escalate":
            status = "escalated"
        else:
            # Fallback for workflows that use `error` only
            status = "success" if not result.get("error") else "failed"

        return {
            "route"      : route,
            "workflow_id": workflow_id,
            "status"     : status,
            "result"     : result,
            "logs"       : result.get("logs", []),
            "error"      : result.get("error"),
        }

    except Exception as e:
        return {
            "route"      : route,
            "workflow_id": workflow_id,
            "status"     : "error",
            "error"      : str(e),
            "logs"       : [],
        }


def invoke_workflows_node(state: dict) -> dict:
    start        = time.time()
    built_states = state.get("built_states", [])

    if not built_states:
        state["logs"].append(
            log("Master Orchestrator", "No workflows to invoke [FAIL]")
        )
        state["error"] = "No built states available"
        return state

    state["logs"].append(log(
        "Master Orchestrator",
        f"Invoking {len(built_states)} workflow(s)..."
    ))

    results = []

    # ── single task — synchronous ────────────────────────
    if len(built_states) == 1:
        item   = built_states[0]
        route  = item["route"]
        wid    = item["workflow_id"]
        result = _invoke_one(route, wid, item["state"])
        results.append(result)

        status_label = "[OK]" if result["status"] == "success" else "[FAIL]"
        state["logs"].append(log(
            "Master Orchestrator",
            f"{route} ({wid}) completed — status={result['status']} {status_label}"
        ))

        # Use 'pending_review' for the orchestrator-level trace when the sub-workflow
        # escalated. This prevents shadowing the W3 agent's own escalated trace which
        # carries the actual HITL options (e.g. ambiguous owner names).
        orch_trace_status = "pending_review" if result["status"] == "escalated" else result["status"]
        write_trace(
            workflow_id   = state.get("workflow_id", "WF-UNKNOWN"),
            workflow_type = "ORCHESTRATOR",
            step_id       = f"invoke_{route}",
            agent         = "master_orchestrator",
            status        = orch_trace_status,
            input_data    = {"workflow_id": wid, "route": route},
            output_data   = {"status": result["status"]},
            log_message   = f"Workflow {route} ({wid}) {result['status']}",
            duration_ms   = int((time.time() - start) * 1000),
        )

    # ── multi-task — parallel ────────────────────────────
    else:
        state["logs"].append(log(
            "Master Orchestrator",
            f"Running {len(built_states)} workflows in parallel..."
        ))

        futures_map = {}

        with ThreadPoolExecutor(max_workers=len(built_states)) as pool:
            for item in built_states:
                future = pool.submit(
                    _invoke_one,
                    item["route"],
                    item["workflow_id"],
                    item["state"],
                )
                futures_map[future] = item

            for future in as_completed(futures_map):
                item   = futures_map[future]
                result = future.result()
                results.append(result)

                status_label = "[OK]" if result["status"] == "success" else "[FAIL]"
                state["logs"].append(log(
                    "Master Orchestrator",
                    f"{item['route']} ({item['workflow_id']}) "
                    f"status={result['status']} {status_label}"
                ))

    state["workflow_results"] = results
    duration = int((time.time() - start) * 1000)
    state["logs"].append(log(
        "Master Orchestrator",
        f"All workflows done in {duration}ms"
    ))

    return state