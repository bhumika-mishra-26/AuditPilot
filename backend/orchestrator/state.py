"""
orchestrator/state.py

Master orchestrator state.
Completely separate from W1/W2/W3 state —
this is the top-level routing layer.
"""

from typing import TypedDict, Optional


class MasterState(TypedDict):
    user_task               : str        # raw text from frontend / main.py
    confidence              : float      # LLM classification confidence 0.0 - 1.0
    route                   : str        # "W1" | "W2" | "W3" | "unclear"
    extracted_params        : dict       # params pulled from user text by LLM
    task_list               : list       # list of tasks if multi-task detected
    needs_clarification     : bool       # True if confidence < threshold
    clarification_question  : str        # question to ask user
    clarification_answer    : str        # user's reply (set by main.py)
    workflow_results        : list       # outcomes from each invoked workflow
    final_reply             : str        # plain-English reply to user
    logs                    : list       # orchestrator-level log lines
    error                   : Optional[str]
    built_states            : list       # states for each workflow to be invoked (ADDED)
    workflow_id             : Optional[str] # tracking ID for the entire run (ADDED)
    is_api_run              : Optional[bool] # True = initiated via API, bypass CLI blocking
    human_resolution        : Optional[str]  # HITL input from dashboard resume