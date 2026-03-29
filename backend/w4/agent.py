"""
w4/agent.py

Cross-workflow pattern memory agent.
Called automatically by W1, W2, W3 whenever an error occurs.

Never called by the master orchestrator directly.
Never touches JSON files.
Only reads and writes SQLite through shared/db.py.

Public API — what other agents import:
    from w4.agent import run_w4

Flow:
    T13 — detect cross-workflow pattern
    T14 — decide retry or escalate using pattern memory
    T15 — raise systemic alert if count >= 3 workflows
    T16 — update pattern memory after every resolution
"""

import time
from shared.db import (
    get_connection,
    write_trace,
    read_pattern,
    update_pattern,
    count_affected_workflows,
    write_systemic_alert,
)
from shared.logger import log, log_step


# ─────────────────────────────────────────────────────────
# THRESHOLD
# If success_rate >= this value → auto retry
# If success_rate <  this value → escalate
# ─────────────────────────────────────────────────────────
RETRY_THRESHOLD = 0.70

# ─────────────────────────────────────────────────────────
# SYSTEMIC THRESHOLD
# If same error appears in this many distinct workflows
# → fire systemic alert
# ─────────────────────────────────────────────────────────
SYSTEMIC_THRESHOLD = 3


# ═════════════════════════════════════════════════════════
# T13 — CROSS-WORKFLOW PATTERN DETECTION
# ═════════════════════════════════════════════════════════

def t13_detect_pattern(error_hash: str) -> dict:
    """
    Queries traces table and counts how many distinct
    workflow_ids have seen this error_hash with status
    failed or escalated.

    Returns
    -------
    {
        "is_systemic"        : bool,
        "count"              : int,
        "affected_workflows" : [workflow_id, ...]
    }
    """
    start = time.time()

    count, affected = count_affected_workflows(error_hash)
    is_systemic = count >= SYSTEMIC_THRESHOLD
    duration = int((time.time() - start) * 1000)

    print(log_step(
        "W4 Agent", "T13_detect_pattern",
        "systemic" if is_systemic else "local",
        "alert" if is_systemic else "continue",
        f"count={count} workflows={affected} duration={duration}ms"
    ))

    return {
        "is_systemic"        : is_systemic,
        "count"              : count,
        "affected_workflows" : affected,
    }


# ═════════════════════════════════════════════════════════
# T14 — READ PATTERN MEMORY + DECIDE ACTION
# ═════════════════════════════════════════════════════════

def t14_get_decision(error_hash: str) -> dict:
    """
    Reads pattern_memory table for this error_hash.
    Compares success_rate against RETRY_THRESHOLD.

    If no prior record exists → defaults to escalate
    (unknown errors are always escalated safely).

    Returns
    -------
    {
        "found"        : bool,
        "decision"     : "retry" | "escalate",
        "success_rate" : float | None,
        "context"      : str | None,
        "reason"       : str,
    }
    """
    start = time.time()
    row   = read_pattern(error_hash)
    duration = int((time.time() - start) * 1000)

    if row is None:
        print(log_step(
            "W4 Agent", "T14_get_decision",
            "no_history",
            "escalate",
            f"error_hash={error_hash} not in pattern_memory — defaulting to escalate"
        ))
        return {
            "found"        : False,
            "decision"     : "escalate",
            "success_rate" : None,
            "context"      : None,
            "reason"       : f"No prior history for {error_hash} — defaulting to escalate",
        }

    rate     = row["success_rate"]
    decision = "retry" if rate >= RETRY_THRESHOLD else "escalate"

    print(log_step(
        "W4 Agent", "T14_get_decision",
        "pattern_found",
        decision,
        f"rate={rate} threshold={RETRY_THRESHOLD} context={row['context']} duration={duration}ms"
    ))

    return {
        "found"        : True,
        "decision"     : decision,
        "success_rate" : rate,
        "context"      : row["context"],
        "reason"       : (
            f"Historical rate {rate:.2f} >= {RETRY_THRESHOLD} → retry"
            if decision == "retry"
            else f"Historical rate {rate:.2f} < {RETRY_THRESHOLD} → escalate"
        ),
    }


# ═════════════════════════════════════════════════════════
# T15 — SYSTEMIC ALERT GENERATION
# ═════════════════════════════════════════════════════════

def t15_raise_systemic_alert(
    error_hash:         str,
    error_type:         str,
    affected_workflows: list[str],
) -> None:
    """
    Fires when T13 detects count >= SYSTEMIC_THRESHOLD.

    Writes one row to systemic_alerts table.
    This row is picked up by the morning briefing module
    and shown as a red banner on the dashboard.

    Parameters
    ----------
    error_hash         : e.g. "hash_503_kyc"
    error_type         : e.g. "HTTP_503_kyc_unavailable"
    affected_workflows : list of workflow_ids e.g. ["WF-C005","WF-PO005","WF-MTG001"]
    """
    context = (
        f"Error {error_type} has occurred {len(affected_workflows)} times "
        f"across {len(affected_workflows)} separate workflows "
        f"({', '.join(affected_workflows)}). "
        f"This is likely a vendor API issue, not a data problem. "
        f"Recommend pausing all workflows dependent on this API "
        f"until vendor confirms resolution."
    )

    write_systemic_alert(
        error_hash         = error_hash,
        error_type         = error_type,
        affected_workflows = affected_workflows,
        context            = context,
    )

    print(log(
        "W4 Agent",
        f"SYSTEMIC ALERT raised — {error_type} across "
        f"{len(affected_workflows)} workflows: {affected_workflows} [ALERT]"
    ))


# ═════════════════════════════════════════════════════════
# T16 — PATTERN MEMORY AUTO-UPDATE
# ═════════════════════════════════════════════════════════

def t16_update_pattern(
    error_hash:      str,
    retry_succeeded: bool = False,
) -> None:
    """
    Called after every resolution — retry or escalation.

    Updates attempts, successes, and success_rate
    in pattern_memory table.

    If the error_hash does not exist in pattern_memory
    (brand new error type) → inserts a new row.

    Parameters
    ----------
    error_hash      : the W4 error hash
    retry_succeeded : True if retry worked, False otherwise
    """
    start = time.time()

    # check if row already exists
    row = read_pattern(error_hash)

    if row is None:
        # brand new error type — insert fresh row
        new_attempts  = 1
        new_successes = 1 if retry_succeeded else 0
        new_rate      = new_successes / new_attempts

        conn = get_connection()
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO pattern_memory
                (error_hash, error_type, agent, recommended_action,
                 attempts, successes, success_rate,
                 last_seen_at, context,
                 systemic_flag, last_systemic_at)
                VALUES (?,?,?,?,?,?,?,datetime('now','localtime'),?,0,NULL)
                """,
                (
                    error_hash,
                    error_hash.replace("hash_", "").upper(),
                    "w4_agent",
                    "retry" if new_rate >= RETRY_THRESHOLD else "escalate",
                    new_attempts,
                    new_successes,
                    new_rate,
                    "New error type — first occurrence recorded",
                ),
            )
            conn.commit()
        finally:
            conn.close()

        print(log_step(
            "W4 Agent", "T16_update_pattern",
            "new_row_created",
            "retry" if new_rate >= RETRY_THRESHOLD else "escalate",
            f"error_hash={error_hash} first_occurrence attempts=1"
        ))
        return

    # existing row — update counts
    update_pattern(error_hash, retry_succeeded)

    # re-read to show updated values
    updated = read_pattern(error_hash)
    duration = int((time.time() - start) * 1000)

    print(log_step(
        "W4 Agent", "T16_update_pattern",
        "updated",
        updated["recommended_action"],
        f"attempts={updated['attempts']} "
        f"successes={updated['successes']} "
        f"rate={updated['success_rate']:.3f} "
        f"duration={duration}ms"
    ))

    # check if rate crossed the threshold for the first time
    old_rate = row["success_rate"]
    new_rate = updated["success_rate"]

    if old_rate < RETRY_THRESHOLD <= new_rate:
        print(log(
            "W4 Agent",
            f"THRESHOLD CROSSED — {error_hash} rate now {new_rate:.2f} "
            f"(was {old_rate:.2f}) — now qualifies for auto-retry [OK]"
        ))
    elif old_rate >= RETRY_THRESHOLD > new_rate:
        print(log(
            "W4 Agent",
            f"THRESHOLD DROPPED — {error_hash} rate now {new_rate:.2f} "
            f"(was {old_rate:.2f}) — switching to escalate [WARN]"
        ))


# ═════════════════════════════════════════════════════════
# run_w4 — MAIN ENTRY POINT
# Called by W1 error_node, W2 orchestrator_node, W3 resolve_owner
# ═════════════════════════════════════════════════════════

def run_w4(
    workflow_id:     str,
    workflow_type:   str,
    error_hash:      str,
    error_type:      str,
    retry_succeeded: bool = False,
) -> dict:
    """
    Main W4 entry point. Runs T13 → T14 → T15 (if systemic) → T16.

    Parameters
    ----------
    workflow_id     : ID of the workflow that hit the error e.g. "WF-C005"
    workflow_type   : "W1" | "W2" | "W3"
    error_hash      : W4 error hash from error_map.py
    error_type      : W4 error type from error_map.py
    retry_succeeded : set True when calling W4 after a retry worked

    Returns
    -------
    {
        "pattern"  : T13 result dict,
        "decision" : T14 result dict,
    }

    The calling agent reads result["decision"]["decision"]
    to know whether to retry or escalate.
    """
    print(log("W4 Agent", f"Activated — workflow={workflow_id} error={error_hash}"))

    # T13 — cross-workflow detection
    pattern = t13_detect_pattern(error_hash)

    # T14 — decision from pattern memory
    decision = t14_get_decision(error_hash)

    # write W4's own decision to traces
    write_trace(
        workflow_id     = workflow_id,
        workflow_type   = "W4",
        step_id         = "T14",
        agent           = "w4_agent",
        status          = "success",
        input_data      = {
            "error_hash"  : error_hash,
            "error_type"  : error_type,
            "is_systemic" : pattern["is_systemic"],
            "count"       : pattern["count"],
        },
        output_data     = {
            "decision"     : decision["decision"],
            "success_rate" : decision["success_rate"],
        },
        error_hash      = error_hash,
        error_type      = error_type,
        decision        = decision["decision"],
        decision_reason = decision["reason"],
    )

    # T15 — systemic alert (only if threshold crossed)
    if pattern["is_systemic"]:
        t15_raise_systemic_alert(
            error_hash         = error_hash,
            error_type         = error_type,
            affected_workflows = pattern["affected_workflows"],
        )

    # T16 — update pattern memory always
    t16_update_pattern(error_hash, retry_succeeded)

    return {
        "pattern"  : pattern,
        "decision" : decision,
    }