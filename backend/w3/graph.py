"""
w3/graph.py

W3 LangGraph StateGraph definition.
Same pattern as W1 and W2 — consistent across all agents.

Flow:
    intake → extraction → owner_resolution → task_writer → END
       ↓           ↓
     error       error → END
"""

from langgraph.graph import END, StateGraph
from w3.state import W3State
from w3.nodes.intake           import intake_node
from w3.nodes.extraction       import extraction_node
from w3.nodes.owner_resolution import owner_resolution_node
from w3.nodes.task_writer      import task_writer_node
from w3.nodes.error            import error_node


# ── routing helpers ──────────────────────────────────────

def route_on_error(state: W3State) -> str:
    return "error" if state.get("error") else "continue"


def route_after_error(state: W3State) -> str:
    """
    After error node runs:
    - if W4 said retry AND error cleared → not implemented
      for W3 (LLM retries are handled inside extraction_node)
    - everything else → end
    """
    return "end"


def route_after_owner_resolution(state: W3State) -> str:
    """
    Owner resolution always continues to task_writer
    even if some tasks were escalated.
    Partial success is still success — write what we can.
    """
    return "task_writer"


# ── build graph ──────────────────────────────────────────

builder = StateGraph(W3State)

builder.add_node("intake",           intake_node)
builder.add_node("extraction",       extraction_node)
builder.add_node("owner_resolution", owner_resolution_node)
builder.add_node("task_writer",      task_writer_node)
builder.add_node("error",            error_node)

builder.set_entry_point("intake")

# intake → error or extraction
builder.add_conditional_edges(
    "intake",
    route_on_error,
    {"error": "error", "continue": "extraction"},
)

# extraction → error or owner_resolution
builder.add_conditional_edges(
    "extraction",
    route_on_error,
    {"error": "error", "continue": "owner_resolution"},
)

# owner_resolution → task_writer always
# (partial success — write assigned tasks even if some escalated)
builder.add_conditional_edges(
    "owner_resolution",
    route_after_owner_resolution,
    {"task_writer": "task_writer"},
)

# task_writer → END
builder.add_edge("task_writer", END)

# error → END
builder.add_conditional_edges(
    "error",
    route_after_error,
    {"end": END},
)

graph = builder.compile()