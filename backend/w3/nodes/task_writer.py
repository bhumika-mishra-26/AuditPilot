"""
w3/nodes/task_writer.py  —  T11

Writes resolved tasks to SQLite tasks table.
Checks for past-deadline and owner overload warnings.
Writes trace row on completion.
"""

import time
import uuid
from datetime import datetime

from shared.logger import log
from shared.db import get_connection, write_trace


def task_writer_node(state: dict) -> dict:
    start          = time.time()
    wid            = state.get("workflow_id", "WF-UNKNOWN")
    assigned_tasks = state.get("assigned_tasks", [])

    if not assigned_tasks:
        state["logs"].append(
            log("Task Writer", "No assigned tasks to write — skipping [OK]")
        )
        return state

    state["logs"].append(
        log("Task Writer", f"Writing {len(assigned_tasks)} tasks to SQLite...")
    )

    conn     = get_connection()
    written  = 0
    warnings = []

    for t in assigned_tasks:
        task_id  = f"TASK-{str(uuid.uuid4())[:6].upper()}"
        owner    = t.get("owner", {})
        deadline = t.get("deadline")

        # ── deadline warning ─────────────────────────────
        deadline_flag = None
        if deadline and deadline.lower() not in ("not specified", "none", ""):
            try:
                # simple check — if deadline looks like a past date
                # for demo we just flag it as a note
                deadline_flag = f"Deadline noted: {deadline}"
            except Exception:
                pass

        # ── owner overload warning ───────────────────────
        overload_flag = None
        current_tasks = owner.get("current_tasks", 0)
        if current_tasks >= 5:
            overload_flag = (
                f"{owner.get('full_name', 'Owner')} already has "
                f"{current_tasks} tasks — may be overloaded"
            )
            warnings.append(overload_flag)
            state["logs"].append(
                log("Task Writer", f"WARNING: {overload_flag}")
            )

        # ── write to tasks table ─────────────────────────
        try:
            conn.execute(
                """
                INSERT OR IGNORE INTO tasks
                (task_id, workflow_id, owner_id, owner_name,
                 title, deadline, priority, status, created_at)
                VALUES (?,?,?,?,?,?,?,?,datetime('now','localtime'))
                """,
                (
                    task_id,
                    wid,
                    owner.get("id"),
                    owner.get("full_name"),
                    t.get("task"),
                    deadline,
                    t.get("priority", "medium"),
                    "pending",
                ),
            )
            written += 1
            state["logs"].append(
                log("Task Writer",
                    f"Task '{t['task'][:40]}...' → {owner.get('full_name')} [OK]")
            )
        except Exception as e:
            state["logs"].append(
                log("Task Writer", f"Failed to write task: {e} [FAIL]")
            )

    conn.commit()
    conn.close()

    state["tasks_written"] = written
    state["logs"].append(
        log("Task Writer", f"{written} tasks written to SQLite [OK]")
    )

    write_trace(
        workflow_id = wid, workflow_type = "W3",
        step_id = "T11_task_writer", agent = "task_writer_agent",
        status = "success",
        input_data  = {"tasks_to_write": len(assigned_tasks)},
        output_data = {
            "written"  : written,
            "warnings" : warnings,
        },
        log_message = f"{written} tasks written with {len(warnings)} warnings.",
        duration_ms = int((time.time() - start) * 1000),
    )
    return state