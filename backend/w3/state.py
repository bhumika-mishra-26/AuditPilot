"""
w3/state.py
W3 State TypedDict — shared across all W3 nodes.
"""

from typing import TypedDict, Optional


class W3State(TypedDict):
    workflow_id     : str
    notes           : str            # raw meeting notes text
    logs            : list
    error           : Optional[str]
    status          : str            # "running" | "completed" | "failed" | "human_required"
    tasks           : list           # extracted tasks from LLM
    assigned_tasks  : list           # tasks with resolved owners
    escalated_tasks : list           # tasks that need human intervention
    human_required  : list           # list of human action items
    tasks_written   : int            # count of tasks written to SQLite
    w4_decision     : Optional[str]  # "retry" | "escalate" — set by error node
    is_api_run      : Optional[bool]
    human_resolution: Optional[str]  # HITL input from dashboard resume