"""
w3/nodes/owner_resolution.py  —  T10

Resolves owner names from tasks to actual team members in the database.

Three outcomes per name:
  resolved  — exactly one match → auto assigned
  ambiguous — two or more match → HITL picks one
  not_found — zero matches      → HITL: add to DB / reassign / skip

W4 called once per error for pattern tracking (only when HITL is genuinely needed).
New members added to team_members table permanently.

KEY FIX: human_resolution is checked BEFORE calling W4 or any blocking input()
to prevent infinite re-escalation loops on API resume runs.
"""

import time
from sqlmodel import Session, select, or_
from shared.db import engine, write_trace
from shared.models import TeamMember
from shared.logger import log
from shared.error_map import get_error_hash
from w4.agent import run_w4

# names that look like owner names but are not real people
INVALID_NAMES = {
    "not specified", "none", "n/a", "tbd", "unknown",
    "not mentioned", "team", "everyone", "all",
}


def _resolve_one(owner_name: str, session: Session) -> dict:
    name_lower = owner_name.lower().strip()
    # Search for full name or partial name matches
    statement = select(TeamMember).where(
        or_(
            TeamMember.full_name.ilike(f"%{name_lower}%"),
            TeamMember.email.ilike(f"%{name_lower}%")
        )
    )
    matches = session.exec(statement).all()

    if len(matches) == 1:
        return {"status": "resolved", "member": matches[0]}
    elif len(matches) > 1:
        return {
            "status" : "ambiguous",
            "matches": matches,
            "reason" : f"Found {len(matches)} people named '{owner_name}'",
        }
    else:
        return {
            "status": "not_found",
            "reason": f"No team member named '{owner_name}'",
        }


def _hitl_ambiguous(owner_name: str, matches: list, task: str, state: dict) -> dict | None:
    """HITL when two or more members match. Human picks one or skips. CLI only."""
    print(f"\n  {'─'*52}")
    print(f"  [HITL] Ambiguous owner — human selection required")
    print(f"  {'─'*52}")
    print(f"  Task : {task[:60]}")
    print(f"  Name : '{owner_name}' matched {len(matches)} people\n")
    for i, m in enumerate(matches, 1):
        print(f"  {i}. {m.full_name:<20} ({m.role})")
    print(f"  {len(matches)+1}. Skip this task")
    print()

    if state.get("is_api_run"):
        return None

    try:
        choice = input("  Your choice: ").strip()
        idx = int(choice) - 1
        if 0 <= idx < len(matches):
            chosen = matches[idx]
            print(f"\n  Assigned to {chosen.full_name} [OK]\n")
            return chosen
        else:
            print(f"\n  Task skipped.\n")
            return None
    except (ValueError, EOFError):
        print(f"\n  Invalid — task skipped.\n")
        return None


def _hitl_not_found(owner_name: str, task: str, state: dict) -> dict | None:
    """
    HITL when name not in team_members table. CLI only.
    Option 1 adds the person permanently to DB.
    """
    print(f"\n  {'─'*52}")
    print(f"  [HITL] Unknown person — human action required")
    print(f"  {'─'*52}")
    print(f"  Task : {task[:60]}")
    print(f"  Name : '{owner_name}' is not in team members\n")
    print(f"  1. Add as new member and assign task")
    print(f"  2. Reassign to an existing team member")
    print(f"  3. Skip this task")
    print()

    if state.get("is_api_run"):
        return None

    try:
        choice = input("  Your choice (1 / 2 / 3): ").strip()
    except EOFError:
        choice = "3"

    if choice == "1":
        email = input(f"  Email for {owner_name} (Enter to auto-generate): ").strip()
        role  = input(f"  Role for {owner_name} (Enter for default): ").strip()

        with Session(engine) as session:
            new_id = f"TM-{owner_name[:3].upper()}-{int(time.time()) % 1000}"
            new_member = TeamMember(
                id=new_id,
                full_name=owner_name.title(),
                email=email if email else f"{owner_name.lower().replace(' ','.')}@company.in",
                role=role if role else "Team Member",
                current_tasks=1
            )
            session.add(new_member)
            session.commit()
            session.refresh(new_member)
            print(f"\n  {new_member.full_name} (ID: {new_id}) added to database [OK]")
            return new_member

    elif choice == "2":
        with Session(engine) as session:
            team = session.exec(select(TeamMember)).all()
            print(f"\n  Existing team members:")
            for i, m in enumerate(team, 1):
                print(f"  {i}. {m.full_name:<20} ({m.role})")
            print()
            try:
                pick = int(input("  Assign to member number: ").strip()) - 1
                if 0 <= pick < len(team):
                    chosen = team[pick]
                    print(f"\n  Reassigned to {chosen.full_name} [OK]\n")
                    return chosen
            except (ValueError, EOFError):
                pass
        print("\n  Invalid — task skipped.\n")
        return None

    else:
        print(f"\n  Task skipped.\n")
        return None


def owner_resolution_node(state: dict) -> dict:
    start = time.time()
    state["error"] = None
    wid   = state.get("workflow_id", "WF-UNKNOWN")
    tasks = state.get("tasks", [])

    state["logs"].append(
        log("Owner Resolution Agent", f"Resolving owners for {len(tasks)} tasks...")
    )

    assigned_tasks  = []
    escalated_tasks = []
    human_required  = []

    with Session(engine) as session:
        for task in tasks:
            t_start    = time.time()
            owner_name = (task.get("owner_name") or "").strip()

            if not owner_name or owner_name.lower() in INVALID_NAMES:
                state["logs"].append(
                    log("Owner Resolution Agent",
                        f"Skipping invalid owner name: '{owner_name}' [OK]")
                )
                continue

            resolution = _resolve_one(owner_name, session)

            # ── clean match ───────────────────────────────────
            if resolution["status"] == "resolved":
                member = resolution["member"]
                assigned_tasks.append({
                    "task"           : task["task"],
                    "owner"          : member.model_dump(),
                    "deadline"       : task.get("deadline"),
                    "priority"       : task.get("priority"),
                    "source_quote"   : task.get("source_quote"),
                    "decision"       : "assigned",
                    "decision_reason": f"Exact match for '{owner_name}'",
                })
                state["logs"].append(
                    log("Owner Resolution Agent",
                        f"'{owner_name}' → {member.full_name} ({member.role}) [OK]")
                )
                write_trace(
                    workflow_id = wid, workflow_type = "W3",
                    step_id = "T10_owner_resolution", agent = "owner_resolution_agent",
                    status = "success",
                    input_data  = {"owner_name": owner_name},
                    output_data = {"member_id": member.id, "member_name": member.full_name},
                    log_message = f"Resolved '{owner_name}' to {member.full_name}",
                    duration_ms = int((time.time() - t_start) * 1000),
                )

            # ── ambiguous — HITL picks one ────────────────────
            elif resolution["status"] == "ambiguous":
                error_hash, error_type = get_error_hash("ambiguous")
                options_str = ", ".join(m.full_name for m in resolution["matches"])

                state["logs"].append(
                    log("Owner Resolution Agent",
                        f"'{owner_name}' is ambiguous — {options_str} — checking resolution [WARN]")
                )

                chosen = None
                hr = state.get("human_resolution") or ""
                if hr:
                    hr_clean = hr.strip().lower()
                    for m in resolution["matches"]:
                        if hr_clean in m.full_name.lower():
                            chosen = m
                            break

                if chosen:
                    assigned_tasks.append({
                        "task"           : task["task"],
                        "owner"          : chosen.model_dump(),
                        "deadline"       : task.get("deadline"),
                        "priority"       : task.get("priority"),
                        "source_quote"   : task.get("source_quote"),
                        "decision"       : "assigned_via_hitl",
                        "decision_reason": f"Human selected {chosen.full_name} from ambiguous match",
                    })
                    state["logs"].append(
                        log("Owner Resolution Agent",
                            f"'{owner_name}' → {chosen.full_name} (human selected) [OK]")
                    )
                    continue

                run_w4(
                    workflow_id    = wid,
                    workflow_type  = "W3",
                    error_hash     = error_hash,
                    error_type     = error_type,
                    retry_succeeded= False,
                )

                if not state.get("is_api_run"):
                    chosen = _hitl_ambiguous(owner_name, resolution["matches"], task["task"], state)

                if chosen:
                    assigned_tasks.append({
                        "task"           : task["task"],
                        "owner"          : chosen.model_dump(),
                        "deadline"       : task.get("deadline"),
                        "priority"       : task.get("priority"),
                        "source_quote"   : task.get("source_quote"),
                        "decision"       : "assigned_via_hitl",
                        "decision_reason": f"Human selected {chosen.full_name} from ambiguous match",
                    })
                else:
                    options_list = [m.full_name for m in resolution["matches"]]
                    escalated_tasks.append({
                        "task"           : task["task"],
                        "owner_searched" : owner_name,
                        "decision"       : "skipped",
                        "human_action"   : f"Choose between: {options_str}",
                    })
                    human_required.append({
                        "step"         : "owner_resolution",
                        "task"         : task["task"],
                        "reason"       : resolution["reason"],
                        "action_needed": f"Choose between: {options_str}",
                    })
                    write_trace(
                        workflow_id=wid, workflow_type="W3",
                        step_id="T10_owner_resolution", agent="owner_resolution_agent",
                        status="escalated",
                        input_data={"owner_name": owner_name},
                        output_data={"options": options_list},
                        error_hash=error_hash, error_type=error_type,
                        decision="escalate", decision_reason="Ambiguous owner"
                    )

            # ── not found — HITL decides ──────────────────────
            else:
                error_hash, error_type = get_error_hash("not_found")
                state["logs"].append(
                    log("Owner Resolution Agent",
                        f"'{owner_name}' not found in database — checking resolution [WARN]")
                )

                chosen = None
                hr = (state.get("human_resolution") or "").strip().lower()

                if hr in ("onboard_member", "add_new_member"):
                    new_id = f"TM-{owner_name[:3].upper()}-{int(time.time()) % 1000}"
                    new_member = TeamMember(
                        id=new_id,
                        full_name=owner_name.title(),
                        email=f"{owner_name.lower().replace(' ','.')}@company.in",
                        role="Team Member",
                        current_tasks=1
                    )
                    session.add(new_member)
                    session.commit()
                    session.refresh(new_member)
                    chosen = new_member
                    state["logs"].append(log("Owner Resolution Agent", f"'{owner_name}' added to DB [OK]"))

                if chosen:
                    assigned_tasks.append({
                        "task"           : task["task"],
                        "owner"          : chosen.model_dump(),
                        "deadline"       : task.get("deadline"),
                        "priority"       : task.get("priority"),
                        "source_quote"   : task.get("source_quote"),
                        "decision"       : "assigned_via_hitl",
                    })
                else:
                    run_w4(
                        workflow_id    = wid,
                        workflow_type  = "W3",
                        error_hash     = error_hash,
                        error_type     = error_type,
                        retry_succeeded= False,
                    )
                    if not state.get("is_api_run"):
                        chosen = _hitl_not_found(owner_name, task["task"], state)
                    
                    if not chosen:
                        human_required.append({
                            "step"         : "owner_resolution",
                            "task"         : task["task"],
                            "reason"       : resolution["reason"],
                            "action_needed": f"Add '{owner_name}' to team or reassign",
                        })
                        write_trace(
                            workflow_id=wid, workflow_type="W3",
                            step_id="T10_owner_resolution", agent="owner_resolution_agent",
                            status="escalated",
                            input_data={"owner_name": owner_name},
                            output_data={"reason": resolution["reason"]},
                            error_hash=error_hash, error_type=error_type,
                            decision="escalate", decision_reason="Owner not found"
                        )

    state["assigned_tasks"]  = assigned_tasks
    state["escalated_tasks"] = escalated_tasks
    state["human_required"]  = human_required
    state["status"] = "escalated" if human_required and state.get("is_api_run") else "completed"

    state["logs"].append(
        log("Owner Resolution Agent",
            f"Done — assigned={len(assigned_tasks)} escalated={len(escalated_tasks)} [OK]")
    )
    return state