"""
w3/nodes/extraction.py

Calls LLM to extract tasks from meeting notes.
Uses OpenRouter API (same as original W3).

On API failure or JSON parse failure — calls W4
instead of managing its own pattern memory.
Writes trace row to SQLite on every outcome.
"""

import time
import json
import os
import httpx
import requests as httpx_requests
from dotenv import load_dotenv
from shared.logger import log
from shared.db import write_trace
from shared.error_map import get_error_hash
from w4.agent import run_w4

load_dotenv()

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL              = "openrouter/auto"
OPENROUTER_URL     = "https://openrouter.ai/api/v1/chat/completions"
MAX_RETRIES        = 3

EXTRACTION_PROMPT = """You are an assistant that extracts action items from meeting notes.

Read these meeting notes and extract every task or action item mentioned.

Meeting notes:
{notes}

Return ONLY a JSON array. No explanation. No markdown. Just the array.
Each item must have exactly these fields:
- task: what needs to be done in one clear sentence
- owner_name: first name of the person responsible exactly as mentioned
- deadline: deadline mentioned or "not specified" if none
- priority: high, medium, or low based on urgency
- source_quote: exact phrase from notes mentioning this task

Example:
[
  {{
    "task": "Update marketing deck with new pricing",
    "owner_name": "Priya",
    "deadline": "this Friday",
    "priority": "high",
    "source_quote": "Priya to update the marketing deck by Friday"
  }}
]"""


def _call_llm(notes: str) -> dict:
    """
    Calls OpenRouter API using requests library.
    Returns {"status": "success", "content": "..."} or
            {"status": "escalate", "reason": "..."}
    """
    for attempt in range(1, MAX_RETRIES + 1):
        start = time.time()
        try:
            print(log("Extraction Agent", f"LLM call attempt {attempt}/{MAX_RETRIES}..."))

            response = httpx_requests.post(
                url     = "https://openrouter.ai/api/v1/chat/completions",
                headers = {
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type" : "application/json",
                },
                json = {
                    "model"   : MODEL,
                    "messages": [
                        {"role": "user", "content": EXTRACTION_PROMPT.format(notes=notes)}
                    ],
                },
                timeout = 30,
            )

            duration = int((time.time() - start) * 1000)
            result   = response.json()

            if "error" in result:
                msg = result["error"].get("message", "unknown error")
                print(log("Extraction Agent", f"API error: {msg}"))
                if attempt < MAX_RETRIES:
                    time.sleep(attempt * 2)
                    continue
                return {"status": "escalate", "reason": f"API error: {msg}", "duration": duration}

            content = result["choices"][0]["message"]["content"].strip()
            return {"status": "success", "content": content, "duration": duration}

        except Exception as e:
            duration = int((time.time() - start) * 1000)
            if attempt < MAX_RETRIES:
                time.sleep(attempt * 2)
                continue
            return {"status": "escalate", "reason": str(e), "duration": duration}

    return {"status": "escalate", "reason": "All retry attempts exhausted", "duration": 0}


def _parse_tasks(raw: str) -> list | None:
    """
    Tries to parse LLM response as JSON array.
    Attempts to extract array if wrapped in other text.
    Returns list on success, None on failure.
    """
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        # try to find the array in the response
        start_idx = raw.find("[")
        end_idx   = raw.rfind("]")
        if start_idx != -1 and end_idx != -1:
            try:
                return json.loads(raw[start_idx:end_idx + 1])
            except json.JSONDecodeError:
                pass
        return None


def extraction_node(state: dict) -> dict:
    start = time.time()
    state["error"] = None
    wid   = state.get("workflow_id", "WF-UNKNOWN")
    notes = state.get("notes", "")

    state["logs"].append(log("Extraction Agent", "Calling LLM to extract tasks..."))

    # ── call LLM ─────────────────────────────────────────
    llm_result = _call_llm(notes)
    duration   = llm_result.get("duration", 0)

    # ── timeout — call W4 ────────────────────────────────
    if llm_result["status"] == "timeout":
        error_hash, error_type = get_error_hash("api_timeout")
        state["logs"].append(
            log("Extraction Agent", f"LLM timed out — calling W4 [FAIL]")
        )
        run_w4(
            workflow_id    = wid,
            workflow_type  = "W3",
            error_hash     = error_hash,
            error_type     = error_type,
            retry_succeeded= False,
        )
        state["error"]  = "api_timeout"
        state["status"] = "failed"
        write_trace(
            workflow_id = wid, workflow_type = "W3",
            step_id = "T9_extraction", agent = "extraction_agent",
            status = "failed",
            input_data  = {"notes_length": len(notes)},
            output_data = {"error": "API timeout"},
            error_hash  = error_hash, error_type = error_type,
            decision = "escalate",
            decision_reason = "LLM API timed out after 3 attempts",
            duration_ms = duration,
        )
        return state

    # ── api error — call W4 ──────────────────────────────
    if llm_result["status"] == "escalate":
        error_hash, error_type = get_error_hash("api_error")
        state["logs"].append(
            log("Extraction Agent", f"LLM API error — calling W4 [FAIL]")
        )
        run_w4(
            workflow_id    = wid,
            workflow_type  = "W3",
            error_hash     = error_hash,
            error_type     = error_type,
            retry_succeeded= False,
        )
        state["error"]  = "api_error"
        state["status"] = "failed"
        write_trace(
            workflow_id = wid, workflow_type = "W3",
            step_id = "T9_extraction", agent = "extraction_agent",
            status = "failed",
            input_data  = {"notes_length": len(notes)},
            output_data = {"error": llm_result["reason"]},
            error_hash  = error_hash, error_type = error_type,
            decision = "escalate",
            decision_reason = llm_result["reason"],
            duration_ms = duration,
        )
        return state

    # ── parse response ───────────────────────────────────
    tasks = _parse_tasks(llm_result["content"])

    if tasks is None:
        error_hash, error_type = get_error_hash("invalid_json")
        state["logs"].append(
            log("Extraction Agent", "Could not parse LLM response as JSON — calling W4 [FAIL]")
        )
        run_w4(
            workflow_id    = wid,
            workflow_type  = "W3",
            error_hash     = error_hash,
            error_type     = error_type,
            retry_succeeded= False,
        )
        state["error"]  = "invalid_json"
        state["status"] = "human_required"
        write_trace(
            workflow_id = wid, workflow_type = "W3",
            step_id = "T9_extraction", agent = "extraction_agent",
            status = "escalated",
            input_data  = {"notes_length": len(notes)},
            output_data = {"error": "JSON parse failed", "raw_response": llm_result["content"][:200]},
            error_hash  = error_hash, error_type = error_type,
            decision = "escalate",
            decision_reason = "LLM returned unparseable JSON — manual task entry needed",
            duration_ms = duration,
        )
        return state

    # ── success ───────────────────────────────────────────
    state["tasks"]  = tasks
    state["logs"].append(
        log("Extraction Agent", f"Extracted {len(tasks)} tasks successfully [OK]")
    )
    write_trace(
        workflow_id = wid, workflow_type = "W3",
        step_id = "T9_extraction", agent = "extraction_agent",
        status = "success",
        input_data  = {"notes_length": len(notes)},
        output_data = {"tasks_found": len(tasks)},
        log_message = f"Extracted {len(tasks)} tasks successfully",
        duration_ms = duration,
    )
    return state