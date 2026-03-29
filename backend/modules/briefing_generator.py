"""
Module 6.2 — Briefing Generator
Takes traces from any workflow, groups them, and writes a morning briefing.
"""

import json
import os
import httpx
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "arcee-ai/trinity-large-preview:free"

def get_salutation() -> str:
    hour = datetime.now().hour
    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"

SYSTEM_PROMPT_TEMPLATE = """You are AuditPilot, an AI operations assistant.
Write a concise briefing for an operations manager.

Rules:
- Start with: "{{salutation}}. Overnight, X workflows ran..." (or similar dynamic start)
- Sort sections: NEEDS YOUR ACTION first, then WATCH, then COMPLETED
- For each workflow: 2-3 sentences max — what happened, what was automatic, what needs a human
- For NEEDS YOUR ACTION: end with exactly what the manager should do
- If everything completed automatically, say so clearly
- Plain English only. Under 250 words total."""


def group_traces(traces: list) -> dict:
    """
    Groups a flat list of trace dicts by workflow_id.
    Handles both DB format (status column) and in-memory format (outcome column).
    Returns { workflow_id: { total, success, failed, escalated, steps[] } }
    """
    groups = {}
    for t in traces:
        wid = t.get("workflow_id", "unknown")
        if wid not in groups:
            groups[wid] = {
                "workflow_id": wid,
                "total": 0,
                "success": 0,
                "failed": 0,
                "escalated": 0,
                "steps": []
            }
        g = groups[wid]
        g["total"] += 1

        # DB uses 'status', in-memory uses 'outcome' — handle both
        outcome = t.get("status") or t.get("outcome", "")
        decision = t.get("decision", "")

        # Skip orchestrator/bookkeeping rows from summary counts
        if t.get("agent") in ("orchestrator", "master_orchestrator"):
            continue

        if outcome == "success":
            g["success"] += 1
        elif decision in ("escalate", "human_required", "ambiguous"):
            g["escalated"] += 1
        else:
            g["failed"] += 1

        g["steps"].append({
            "agent":    t.get("agent", ""),
            "action":   t.get("action") or t.get("step_id", ""),
            "outcome":  outcome,
            "decision": decision,
            "reason":   t.get("reason") or t.get("decision_reason", "")
        })

    return groups


def get_traces_from_db(hours: int = 8) -> list:
    """
    Pulls all traces from the last N hours from DB.
    Used by the scheduler to get overnight activity automatically.
    """
    import sys
    from pathlib import Path
    
    # Ensure root is in sys.path
    root = Path(__file__).resolve().parent.parent
    if str(root) not in sys.path:
        sys.path.append(str(root))
        
    from shared.db import get_connection

    try:
        conn = get_connection()
        # Pull the last 150 rows within the timeframe to avoid overwhelming the LLM
        rows = conn.execute("""
            SELECT * FROM (
                SELECT * FROM traces
                WHERE created_at >= datetime('now', ?)
                ORDER BY created_at DESC
                LIMIT 150
            ) ORDER BY created_at ASC
        """, (f"-{hours} hours",)).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[briefing] Could not read from DB: {e}")
        return []


def generate_briefing(traces: list) -> dict:
    """
    Main function. Pass in a list of trace dicts from any workflow.
    Returns:
    {
      "briefing_text": "Good morning...",
      "workflow_count": 3,
      "needs_action_count": 1,
      "generated_at": "2026-03-21 08:45"
    }
    """
    salutation = get_salutation()
    
    if not traces:
        return {
            "briefing_text": (
                f"{salutation}.\n\n"
                "No workflow activity was recorded overnight. "
                "AuditPilot is standing by.\n\n"
                "— AuditPilot"
            ),
            "workflow_count": 0,
            "needs_action_count": 0,
            "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M")
        }

    groups = group_traces(traces)

    needs_action_count = sum(
        1 for g in groups.values() if g["escalated"] > 0
    )

    # Build compact summary for the prompt
    workflow_summaries = []
    for wid, g in groups.items():
        workflow_summaries.append({
            "workflow_id":     wid,
            "steps_total":     g["total"],
            "steps_success":   g["success"],
            "steps_failed":    g["failed"],
            "steps_escalated": g["escalated"],
            "status": (
                "needs_action" if g["escalated"] > 0
                else "failed"  if g["failed"] > 0
                else "completed"
            ),
            "recent_actions": [
                f"{s['agent']}: {s['reason'] or s['outcome']}" 
                for s in g["steps"][-3:]
            ]
        })

    payload = {
        "date":      datetime.now().strftime("%A, %B %d %Y"),
        "workflows": workflow_summaries
    }

    prompt = (
        f"Here is the overnight activity:\n\n"
        f"{json.dumps(payload, indent=2)}\n\n"
        f"Write the morning briefing now."
    )

    try:
        response = httpx.post(
            url="https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json"
            },
            json={
                "model": MODEL,
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT_TEMPLATE.replace("{{salutation}}", salutation)},
                    {"role": "user",   "content": prompt}
                ]
            },
            timeout=30
        )

        result = response.json()

        if "error" in result:
            briefing_text = f"Briefing generation failed: {result['error'].get('message', 'unknown')}"
        else:
            briefing_text = result["choices"][0]["message"]["content"].strip()

    except httpx.TimeoutException:
        briefing_text = "Briefing generation timed out. Check your connection."
    except Exception as e:
        briefing_text = f"Briefing generation failed: {str(e)}"

    return {
        "briefing_text":      briefing_text,
        "workflow_count":     len(groups),
        "needs_action_count": needs_action_count,
        "generated_at":       datetime.now().strftime("%Y-%m-%d %H:%M")
    }


# Quick test — run directly to verify
if __name__ == "__main__":
    # Test 1 — sample traces (no DB needed)
    print("── Test 1: sample traces ────────────────────────────")
    sample_traces = [
        {
            "workflow_id": "wf_meeting_001",
            "agent": "intake_agent",
            "status": "success",
            "decision": "continue",
            "decision_reason": "42 words — validation passed"
        },
        {
            "workflow_id": "wf_meeting_001",
            "agent": "extraction_agent",
            "status": "success",
            "decision": "continue",
            "decision_reason": "3 tasks extracted"
        },
        {
            "workflow_id": "wf_meeting_001",
            "agent": "owner_resolution",
            "status": "ambiguous",
            "decision": "human_required",
            "decision_reason": "Multiple matches: Rahul Sharma, Rahul Verma"
        },
        {
            "workflow_id": "wf_vendor_002",
            "agent": "intake_agent",
            "status": "success",
            "decision": "continue",
            "decision_reason": "Vendor ID found"
        },
        {
            "workflow_id": "wf_vendor_002",
            "agent": "kyc_agent",
            "status": "success",
            "decision": "continue",
            "decision_reason": "KYC verified automatically"
        }
    ]

    result = generate_briefing(sample_traces)
    print(f"Workflows: {result['workflow_count']}  |  Needs action: {result['needs_action_count']}")
    print(f"Generated at: {result['generated_at']}")
    print("─" * 55)
    print(result["briefing_text"])