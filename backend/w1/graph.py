"""
w1/graph.py

W1 LangGraph StateGraph definition.
Connects all 5 nodes with conditional routing.
"""

from langgraph.graph import END, StateGraph
from w1.state import W1State
from w1.nodes.validation import validate_node
from w1.nodes.duplicate  import duplicate_node
from w1.nodes.kyc        import kyc_node
from w1.nodes.execution  import create_account_node
from w1.nodes.error      import error_node


# ── routing helpers ──────────────────────────────────────

def route_on_error(state: W1State) -> str:
    return "error" if state.get("error") else "continue"


def route_after_kyc(state: W1State) -> str:
    if state.get("error"):
        return "error"
    return "create_account"


def route_after_error(state: W1State) -> str:
    # W4 said retry AND error was cleared → go back to kyc
    if state.get("retry_count", 0) >= 1 and state.get("error") is None:
        return "kyc"
    # Merged with existing or override approved → go back to kyc
    if (state.get("w4_decision") == "merge" or state.get("skip_kyc")) and state.get("error") is None:
        return "kyc"
    return "end"


def route_after_create(state: W1State) -> str:
    return "error" if state.get("error") else "end"


# ── build graph ──────────────────────────────────────────

builder = StateGraph(W1State)

builder.add_node("validate",       validate_node)
builder.add_node("duplicate",      duplicate_node)
builder.add_node("kyc",            kyc_node)
builder.add_node("create_account", create_account_node)
builder.add_node("error",          error_node)

builder.set_entry_point("validate")

builder.add_conditional_edges(
    "validate", route_on_error,
    {"error": "error", "continue": "duplicate"},
)

builder.add_conditional_edges(
    "duplicate", route_on_error,
    {"error": "error", "continue": "kyc"},
)

builder.add_conditional_edges(
    "kyc", route_after_kyc,
    {"error": "error", "create_account": "create_account"},
)

builder.add_conditional_edges(
    "error", route_after_error,
    {"kyc": "kyc", "end": END},
)

builder.add_conditional_edges(
    "create_account", route_after_create,
    {"error": "error", "end": END},
)

graph = builder.compile()