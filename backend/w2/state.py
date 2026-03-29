"""
w2/state.py
W2 State TypedDict — shared across all W2 nodes.
"""

from typing import TypedDict, Optional


class W2State(TypedDict):
    workflow_id  : str
    input        : dict        # raw PO data from purchase_orders.json
    logs         : list
    error        : Optional[str]
    approved     : bool        # set True by approval_node
    retry_count  : int
    status       : str         # "running" | "completed" | "failed"
    w4_decision  : Optional[str]  # "retry" | "escalate" — set by orchestrator
    hitl_enabled : bool        # True = show human approval prompts in terminal
    is_api_run   : Optional[bool]