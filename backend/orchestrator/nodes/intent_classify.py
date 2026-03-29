"""
orchestrator/nodes/intent_classify.py

Calls OpenRouter API to classify the user's task.
Returns route, confidence, extracted params,
and whether multiple tasks were detected.

If clarification answer is present in state
(user replied to a previous question),
it is appended to the original task before classification.
"""

import json
import time
import os
import urllib.request
import urllib.error

from dotenv import load_dotenv
from shared.logger import log
from shared.utils import classify_task_keywords
from shared.db import write_trace

load_dotenv()

OPENROUTER_API_KEY   = os.environ.get("OPENROUTER_API_KEY", "")
MODEL                = "openrouter/auto"
OPENROUTER_URL       = "https://openrouter.ai/api/v1/chat/completions"
CONFIDENCE_THRESHOLD = 0.85

SYSTEM_PROMPT = """You are a workflow router for AuditPilot — a business process automation system.

You have exactly 3 workflows available:

W1 — Client onboarding
  Use when: user wants to onboard, register, add, or create a new client or company.
  Examples: "onboard Krishna Logistics", "add new client Mehta Textiles", "register a company"

W2 — Procurement to payment
  Use when: user wants to process a purchase order, make a payment, pay a vendor,
  approve an invoice, or handle any financial transaction with a supplier.
  Examples: "pay Tata Steels", "process PO-2024-001", "approve invoice from Sharma Industries"

W3 — Meeting to task
  Use when: user wants to convert meeting notes into tasks, assign action items
  from a meeting, or extract and assign tasks from any unstructured text.
  Examples: "assign tasks from today's meeting", "extract action items", "meeting notes: ..."

Return ONLY valid JSON. No explanation. No markdown. Just the SINGLE JSON object. 
Strictly avoid providing multiple examples or alternatives.

Format:
{
  "route": "W1" | "W2" | "W3" | "unclear",
  "confidence": 0.0 to 1.0,
  "extracted_params": {
    "client_name": "...", "email": "...", "gstin": "...", "phone": "...",
    "vendor_name": "...", "po_number": "...", "amount": 0, "vendor_id": "...",
    "notes": "..."
  },
  "task_list": [
    {"route": "W1", "extracted_params": {...}},
    {"route": "W2", "extracted_params": {...}}
  ],
  "is_multi_task": false,
  "clarification_question": "only set this if route is unclear"
}

If the task mentions two separate workflows (e.g. "onboard X and pay Y"),
set is_multi_task=true and populate task_list with both tasks.
Set route to the first task's route in that case.

CRITICAL RULE FOR W3:
If the user provides meeting notes, action items, or a transcript to extract tasks from, it is PURELY a W3 task. DO NOT set is_multi_task=true even if the notes mention onboarding (W1) or payments (W2). Do not split it. Return route="W3", is_multi_task=false, and put the ENTIRE text in extracted_params.notes.

If you cannot determine the workflow with confidence >= 0.85,
set route="unclear" and provide a clarification_question.
Do NOT output anything else."""


def fix_escapes(s: str) -> str:
    """
    Fix common LLM JSON escaping issues.
    Specifically handles hallucinations like \_ which is not valid JSON.
    """
    import re
    # Remove backslashes that are NOT followed by a valid JSON escape char (n, r, t, ", \, /)
    # Valid escapes in JSON: \", \\, \/, \b, \f, \n, \r, \t, \uXXXX
    # This regex looks for a backslash followed by a character NOT in [nrt"\/bf]
    s = re.sub(r'\\(?![nrt"\\/bf])', '', s)
    return s

def _call_openrouter(prompt: str) -> dict:

    """
    Calls OpenRouter API using urllib (no requests/httpx dependency).
    Returns parsed JSON dict or raises on error.
    """
    payload = json.dumps({
        "model"   : MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user",   "content": prompt},
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

    raw = body["choices"][0]["message"]["content"].strip()

    # 1. Try direct parse
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        pass

    # 2. Strip markdown fences if present
    processed = raw
    if "```" in processed:
        # handle cases where there is text before the code block
        parts = processed.split("```")
        for part in parts:
            if part.strip().startswith("{") or part.strip().startswith("json"):
                processed = part.strip()
                if processed.startswith("json"):
                    processed = processed[4:].strip()
                break

    # 3. Last resort: regex to find first { and last }
    import re
    match = re.search(r"(\{.*\})", processed, re.DOTALL)
    if match:
        processed = match.group(1)

    # 5. Handle "or" separator if LLM hallucinated multiple examples
    if "\n\nor\n\n" in processed:
        # Just pick the first one
        processed = processed.split("\n\nor\n\n")[0].strip()

    try:
        return json.loads(processed)
    except json.JSONDecodeError:
        # try one more time with fixed escapes
        try:
            return json.loads(fix_escapes(processed))
        except json.JSONDecodeError as e:
            # log the raw for debugging before re-raising
            from shared.logger import log
            # we can't easily return this log to the state from here,
            # so we'll just raise and let the node handle it
            print(f"DEBUG: RAW LLM RESPONSE: {raw}")
            raise e


def intent_classify_node(state: dict) -> dict:
    start = time.time()

    # Bypass classification if tasks are already provided (Demo mode or direct API)
    if state.get("task_list") or state.get("route"):
        state["logs"].append(log("Master Orchestrator", "Task already classified, skipping LLM [OK]"))
        state["needs_clarification"] = False
        return state

    task  = state.get("user_task", "")

    # ── skip classification if demo mode pre-set the task list ──
    if state.get("task_list") and len(state["task_list"]) > 0:
        state["logs"].append(log("Master Orchestrator", "Task already classified (pre-set) [OK]"))
        state["needs_clarification"] = False
        return state

    # if user answered a clarification question — append their answer
    if state.get("clarification_answer"):
        task = f"{task}\nUser clarification: {state['clarification_answer']}"

    state["logs"].append(
        log("Master Orchestrator", f"Classifying task: '{task[:60]}...'")
    )

    try:
        result = _call_openrouter(task)

        route      = result.get("route", "unclear")
        confidence = result.get("confidence", 0.0)
        params     = result.get("extracted_params", {})
        is_multi   = result.get("is_multi_task", False)
        task_list  = result.get("task_list", [])
        clarq      = result.get("clarification_question", "")

        # ── Hard fix for W3 multi-task hallucination ──────────
        # Meeting notes often contain phrases like "call client" or "pay vendor".
        # If the LLM splits these out into W1/W2, the W3 extraction fails or misses context.
        if route == "W3" or (is_multi and any(t.get("route") == "W3" for t in task_list)):
            state["logs"].append(log("Master Orchestrator", "W3 text detected — forcing single task so notes remain intact [OK]"))
            route = "W3"
            is_multi = False
            task_list = []
            if not params.get("notes"):
                params["notes"] = task

        # ── fallback to keywords if LLM is unclear ──────────
        if route == "unclear" or confidence < 0.5:
            kw_result = classify_task_keywords(task)
            if kw_result["route"] != "unclear" and kw_result["confidence"] > confidence:
                state["logs"].append(log("Master Orchestrator", "LLM unclear — falling back to keyword classifier [OK]"))
                route      = kw_result["route"]
                confidence = kw_result["confidence"]
                params     = kw_result["extracted_params"]
                is_multi   = kw_result["is_multi"]
                task_list  = kw_result["task_list"]

        state["route"]            = route
        state["confidence"]       = confidence
        state["extracted_params"] = params
        state["task_list"]        = task_list if is_multi else [{"route": route, "extracted_params": params}]

        duration = int((time.time() - start) * 1000)

        if route == "unclear" or confidence < CONFIDENCE_THRESHOLD:
            state["needs_clarification"]    = True
            state["clarification_question"] = clarq or "Could you clarify — are you onboarding a client, processing a payment, or assigning meeting tasks?"
            state["logs"].append(log(
                "Master Orchestrator",
                f"Low confidence ({confidence}) — clarification needed [WARN]"
            ))
        else:
            state["needs_clarification"] = False
            multi_label = f" (multi-task: {len(task_list)} tasks)" if is_multi else ""
            state["logs"].append(log(
                "Master Orchestrator",
                f"Route={route} confidence={confidence}{multi_label} "
                f"params={list(params.keys())} [{duration}ms] [OK]"
            ))

            write_trace(
                workflow_id   = state.get("workflow_id", "WF-UNKNOWN"),
                workflow_type = "ORCHESTRATOR",
                step_id       = "intent_classification",
                agent         = "master_orchestrator",
                status        = "success",
                input_data    = {"user_task": task[:100]},
                output_data   = {"route": route, "confidence": confidence},
                log_message   = f"Classified task as {route} (confidence={confidence})",
                duration_ms   = duration,
            )

    except urllib.error.URLError as e:
        state["logs"].append(log("Master Orchestrator", f"API call failed: {e} [FAIL]"))
        state["route"]      = "unclear"
        state["confidence"] = 0.0
        state["needs_clarification"]    = True
        state["clarification_question"] = "I could not reach the classification service. Please specify: onboard a client / process a payment / assign meeting tasks?"
        state["error"] = str(e)

    except (json.JSONDecodeError, KeyError) as e:
        state["logs"].append(log("Master Orchestrator", f"Parse error: {e} [FAIL]"))
        state["route"]      = "unclear"
        state["confidence"] = 0.0
        state["needs_clarification"]    = True
        state["clarification_question"] = "I could not understand the task. Please specify: onboard a client / process a payment / assign meeting tasks?"
        state["error"] = str(e)

    return state