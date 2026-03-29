"""
w2/graph.py
W2 LangGraph StateGraph definition.
"""

from langgraph.graph import END, StateGraph
from w2.state import W2State
from w2.nodes.intake       import intake_node
from w2.nodes.validation   import validation_node
from w2.nodes.vendor_check import vendor_check_node
from w2.nodes.approval     import approval_node
from w2.nodes.payment      import payment_node
from w2.nodes.monitor      import monitor_node
from w2.nodes.orchestrator import orchestrator_node
from w2.nodes.audit        import audit_node


# ── routing helpers ──────────────────────────────────────

def route_after_orchestrator(state: W2State) -> str:
    # W4 said retry and retry_count is now 1 → go back to payment
    if state.get("retry_count", 0) == 1 and state.get("status") == "running":
        return "payment"
    return "audit"


# ── build graph ──────────────────────────────────────────

builder = StateGraph(W2State)

builder.add_node("intake",        intake_node)
builder.add_node("validation",    validation_node)
builder.add_node("vendor_check",  vendor_check_node)
builder.add_node("approval",      approval_node)
builder.add_node("payment",       payment_node)
builder.add_node("monitor",       monitor_node)
builder.add_node("orchestrator",  orchestrator_node)
builder.add_node("audit",         audit_node)

builder.set_entry_point("intake")

builder.add_edge("intake",       "validation")
builder.add_edge("validation",   "vendor_check")
builder.add_edge("vendor_check", "approval")
builder.add_edge("approval",     "payment")
builder.add_edge("payment",      "monitor")
builder.add_edge("monitor",      "orchestrator")

builder.add_conditional_edges(
    "orchestrator",
    route_after_orchestrator,
    {"payment": "payment", "audit": "audit"},
)

builder.add_edge("audit", END)

graph = builder.compile()