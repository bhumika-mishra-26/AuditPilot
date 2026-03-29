"""
w1/state.py

W1 State TypedDict — shared across all W1 nodes.
Every node reads from and writes to this dict.
"""

from typing import TypedDict, Optional


class W1State(TypedDict):
    workflow_id  : str           # e.g. "WF-C001" — set by main.py before invoke
    input        : dict          # raw client data from clients.json
    logs         : list          # terminal log lines — printed at end of run
    error        : Optional[str] # set by any node on failure, cleared on retry
    retry_count  : int           # incremented by error_node on retry
    kyc_status   : bool          # set True by kyc_node on success
    hitl_enabled : bool          # True = show ask_choice prompts
    skip_kyc     : bool          # True = human approved KYC override
    w4_decision  : Optional[str] # "retry" | "escalate" — set by error_node after W4
    is_api_run   : Optional[bool]# True = bypass terminal prompts and return escalation states