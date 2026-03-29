"""
shared/logger.py

Single log formatter used by every agent.
Includes live_print() for real-time terminal output
showing exactly which agent is running and what step.
"""

from datetime import datetime
import sys

# ── ANSI colour codes (Windows 10+ supports these) ───────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"

# agent colours
C_ORCH  = "\033[94m"   # bright blue  — master orchestrator
C_W1    = "\033[92m"   # bright green — W1
C_W2    = "\033[96m"   # bright cyan  — W2
C_W3    = "\033[95m"   # bright magenta — W3
C_W4    = "\033[93m"   # bright yellow — W4
C_OK    = "\033[32m"   # green  — success
C_FAIL  = "\033[31m"   # red    — failure
C_WARN  = "\033[33m"   # yellow — warning
C_DIM   = "\033[2m"    # dim    — background info

# map agent name prefixes to colours
AGENT_COLORS = {
    "Master"      : C_ORCH,
    "Orchestrator": C_ORCH,
    "W4"          : C_W4,
    "W4 Agent"    : C_W4,
    "Validation"  : C_W1,
    "Intake"      : C_W1,
    "KYC"         : C_W1,
    "Execution"   : C_W1,
    "Duplicate"   : C_W1,
    "Vendor"      : C_W2,
    "Approval"    : C_W2,
    "Payment"     : C_W2,
    "Monitor"     : C_W2,
    "Audit"       : C_W2,
    "Extraction"  : C_W3,
    "Owner"       : C_W3,
    "Task Writer" : C_W3,
    "Explainability": C_W4,
    "Escalation"  : C_WARN,
}


def _agent_color(agent: str) -> str:
    for prefix, color in AGENT_COLORS.items():
        if prefix.lower() in agent.lower():
            return color
    return RESET


def _status_color(message: str) -> str:
    if "[OK]" in message:      return C_OK
    if "[FAIL]" in message:    return C_FAIL
    if "[WARN]" in message:    return C_WARN
    if "[RETRY]" in message:   return C_WARN
    if "[ALERT]" in message:   return C_FAIL
    return RESET


def live_print(agent: str, message: str) -> None:
    """
    Prints agent activity IMMEDIATELY to terminal
    with colour coding so you can watch the flow live.

    Call this instead of print(log(...)) inside nodes
    when you want real-time visibility.
    """
    timestamp  = datetime.now().strftime("%H:%M:%S")
    ac         = _agent_color(agent)
    sc         = _status_color(message)
    msg_color  = sc if sc != RESET else ""

    line = (
        f"{DIM}[{timestamp}]{RESET} "
        f"{ac}{BOLD}[{agent}]{RESET} "
        f"{msg_color}{message}{RESET}"
    )
    print(line, flush=True)


def log(agent: str, message: str) -> str:
    """
    Formats a log line AND prints it live to terminal immediately.
    Returns the formatted string so it is also stored in state["logs"].

    Every node does:  state["logs"].append(log("Agent", "message"))
    This single call now does both — prints live AND stores the line.
    No node files need to be changed.
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    formatted = f"[{timestamp}] [{agent}] {message}"

    ac        = _agent_color(agent)
    sc        = _status_color(message)
    mc        = sc if sc != RESET else ""
    print(
        f"{DIM}[{timestamp}]{RESET} "
        f"{ac}{BOLD}[{agent}]{RESET} "
        f"{mc}{message}{RESET}",
        flush=True,
    )

    return formatted


def log_step(
    agent:    str,
    action:   str,
    outcome:  str,
    decision: str = None,
    reason:   str = None,
) -> str:
    """
    Formats a structured step log line.
    Matches the format W3 was using in its log_trace() function.

    Output format:
        [HH:MM:SS] [Agent] action → outcome | decision | reason

    Examples
    --------
    log_step("KYC Agent", "kyc_verify", "failed", "retry", "rate 0.87 above threshold")
        → "[14:23:02] [KYC Agent] kyc_verify → failed | retry | rate 0.87 above threshold"

    log_step("W4 Agent", "pattern_check", "systemic", "alert", "3 workflows affected")
        → "[14:23:03] [W4 Agent] pattern_check → systemic | alert | 3 workflows affected"
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    base = f"[{timestamp}] [{agent}] {action} → {outcome}"

    if decision:
        base += f" | {decision}"
    if reason:
        base += f" | {reason}"

    return base


def log_section(title: str) -> str:
    """
    Prints a section separator for readable terminal output.

    Example
    -------
    log_section("W1 Client Onboarding — C-005 Gupta Pharma")
        → "══════════════════════════════════════════════════"
           "  W1 Client Onboarding — C-005 Gupta Pharma"
           "══════════════════════════════════════════════════"
    """
    width = 54
    line  = "═" * width
    return f"\n{line}\n  {title}\n{line}"