"""
orchestrator/graph.py

Master orchestrator LangGraph StateGraph.

Flow:
  intent_classify
      ↓ confident
  state_builder → invoke_workflows → result_builder → END
      ↓ unclear
  clarification → intent_classify (loop until confident)
"""

from langgraph.graph import END, StateGraph
from orchestrator.state import MasterState
from orchestrator.nodes.intent_classify  import intent_classify_node
from orchestrator.nodes.clarification    import clarification_node
from orchestrator.nodes.state_builder    import state_builder_node
from orchestrator.nodes.invoke_workflows import invoke_workflows_node
from orchestrator.nodes.result_builder   import result_builder_node


# ── routing helpers ──────────────────────────────────────

def route_after_classify(state: MasterState) -> str:
    if state.get("error"):
        return "end"
    if state.get("needs_clarification"):
        return "clarification"
    return "state_builder"


def route_after_clarification(state: MasterState) -> str:
    if state.get("error"):
        return "end"
    return "intent_classify"


# ── build graph ──────────────────────────────────────────

builder = StateGraph(MasterState)

builder.add_node("intent_classify",  intent_classify_node)
builder.add_node("clarification",    clarification_node)
builder.add_node("state_builder",    state_builder_node)
builder.add_node("invoke_workflows", invoke_workflows_node)
builder.add_node("result_builder",   result_builder_node)

builder.set_entry_point("intent_classify")

builder.add_conditional_edges(
    "intent_classify",
    route_after_classify,
    {
        "clarification": "clarification",
        "state_builder": "state_builder",
        "end"          : END,
    },
)

builder.add_conditional_edges(
    "clarification",
    route_after_clarification,
    {
        "intent_classify": "intent_classify",
        "end"            : END,
    },
)

builder.add_edge("state_builder",    "invoke_workflows")
builder.add_edge("invoke_workflows", "result_builder")
builder.add_edge("result_builder",   END)

graph = builder.compile()