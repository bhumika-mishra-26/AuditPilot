"""
orchestrator/nodes/clarification.py

Asks the user a clarification question when
confidence is below threshold or route is unclear.

In terminal mode — uses input().
In API mode — returns the question so the
frontend can display it and collect the answer.
"""

from shared.logger import log


def clarification_node(state: dict) -> dict:
    question = state.get(
        "clarification_question",
        "Could you clarify what you want to do?"
    )

    state["logs"].append(
        log("Master Orchestrator", f"Asking for clarification: {question}")
    )

    if state.get("is_api_run"):
        # For API runs, we skip the blocking input() and return 'pending_review'
        # The frontend will detect this and show an intervention UI.
        state["status"] = "pending_review"
        state["logs"].append(log("Master Orchestrator", "Waiting for human clarification via API..."))
        return state

    print(f"\n[Master Orchestrator] {question}")

    try:
        answer = input("  Your answer: ").strip()
    except EOFError:
        # non-interactive mode — use a default
        answer = ""

    if answer:
        state["clarification_answer"] = answer
        state["logs"].append(
            log("Master Orchestrator", f"User replied: '{answer}' [OK]")
        )
    else:
        # no answer — force escalation
        state["clarification_answer"] = ""
        state["logs"].append(
            log("Master Orchestrator", "No clarification received — cannot route [FAIL]")
        )
        state["error"] = "No clarification provided"

    # reset clarification flag so intent_classify re-evaluates
    state["needs_clarification"] = False

    return state