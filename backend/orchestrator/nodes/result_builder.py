"""
orchestrator/nodes/result_builder.py

Builds a plain-English reply from all workflow results.
Calls OpenRouter API to generate a natural language summary.

Falls back to a structured text summary if API is unavailable.
"""

import json
import time
import os
import urllib.request
import urllib.error

from dotenv import load_dotenv
from shared.logger import log
from shared.db import write_trace

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL              = "openrouter/auto"
OPENROUTER_URL     = "https://openrouter.ai/api/v1/chat/completions"

RESULT_PROMPT = """You are AuditPilot, a business process automation assistant.
A user submitted a task and one or more workflows ran to completion.
Write a clear, concise, plain-English summary of what happened.

User task: {user_task}

Workflow results:
{results_json}

Rules:
- 2-4 sentences maximum
- Be specific — include names, IDs, amounts if present in the results
- If successful: confirm what was done
- If failed or escalated: explain why and what the user should do next
- Never use bullet points — write in prose only
- Sound like a helpful assistant, not a system log"""


def _call_openrouter(user_task: str, results: list) -> str:
    """
    Calls OpenRouter API to generate plain-English summary.
    Returns the summary string.
    """

    # build a clean summary of results for the prompt
    clean_results = []
    for r in results:
        item = {
            "workflow"   : r.get("route"),
            "workflow_id": r.get("workflow_id"),
            "status"     : r.get("status"),
        }
        if r.get("error"):
            item["error"] = r["error"]

        result_data = r.get("result", {})
        if result_data:
            route = r.get("route")
            if route == "W1":
                item["client_id"]   = result_data.get("input", {}).get("client_id")
                item["kyc_status"]  = result_data.get("kyc_status")
                item["w4_decision"] = result_data.get("w4_decision")
            elif route == "W2":
                item["po_no"]        = result_data.get("input", {}).get("po_no")
                item["final_status"] = result_data.get("status")
                item["retry_count"]  = result_data.get("retry_count")
                item["w4_decision"]  = result_data.get("w4_decision")
            elif route == "W3":
                item["assigned"]  = len(result_data.get("assigned_tasks", []))
                item["escalated"] = len(result_data.get("escalated_tasks", []))
                item["written"]   = result_data.get("tasks_written", 0)

        clean_results.append(item)

    payload = json.dumps({
        "model"   : MODEL,
        "messages": [
            {
                "role"   : "user",
                "content": RESULT_PROMPT.format(
                    user_task    = user_task,
                    results_json = json.dumps(clean_results, indent=2),
                ),
            }
        ],
    }).encode("utf-8")

    req = urllib.request.Request(
        OPENROUTER_URL,
        data    = payload,
        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type" : "application/json",
        },
        method = "POST",
    )

    with urllib.request.urlopen(req, timeout=30) as resp:
        body = json.loads(resp.read().decode("utf-8"))

    return body["choices"][0]["message"]["content"].strip()


def _fallback_reply(results: list) -> str:
    """
    Builds a plain-text summary without Claude API.
    Used when API is unavailable.
    """
    lines = []
    for r in results:
        route  = r.get("route", "?")
        status = r.get("status", "unknown")
        wid    = r.get("workflow_id", "")

        if status == "success":
            lines.append(f"{route} ({wid}) completed successfully.")
        elif status == "failed":
            err = r.get("error", "unknown error")
            lines.append(f"{route} ({wid}) failed — {err}. Please check the morning briefing for details.")
        else:
            lines.append(f"{route} ({wid}) ended with status: {status}.")

    return " ".join(lines) if lines else "Workflow completed. Check traces for details."


def result_builder_node(state: dict) -> dict:
    start   = time.time()
    results = state.get("workflow_results", [])

    state["logs"].append(
        log("Master Orchestrator", "Building plain-English result summary...")
    )

    try:
        reply = _call_openrouter(state.get("user_task", ""), results)
        state["logs"].append(log(
            "Master Orchestrator",
            f"Result summary generated via Claude API [OK]"
        ))

    except (urllib.error.URLError, KeyError, json.JSONDecodeError) as e:
        # graceful fallback — don't fail just because result builder can't reach API
        reply = _fallback_reply(results)
        state["logs"].append(log(
            "Master Orchestrator",
            f"Claude API unavailable — using fallback summary [WARN]"
        ))

    state["final_reply"] = reply
    duration = int((time.time() - start) * 1000)

    state["logs"].append(log(
        "Master Orchestrator",
        f"Final reply ready [{duration}ms] [OK]"
    ))

    write_trace(
        workflow_id   = state.get("workflow_id", "WF-UNKNOWN"),
        workflow_type = "ORCHESTRATOR",
        step_id       = "result_summary",
        agent         = "master_orchestrator",
        status        = "success",
        input_data    = {"results_count": len(results)},
        output_data   = {"summary_length": len(reply), "final_reply": reply},
        log_message   = "Generated final plain-English summary",
        duration_ms   = duration,
    )

    print(f"\n[AuditPilot] {reply}\n")

    return state