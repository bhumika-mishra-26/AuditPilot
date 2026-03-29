"""
Module 6.1 — Ask-Why Engine
Explains any agent decision in plain English.
"""

import json
import httpx
import os
import sys
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
MODEL = "arcee-ai/trinity-large-preview:free"

SYSTEM_PROMPT = """You are an audit assistant for AuditPilot, an AI workflow system.
Explain agent decisions in plain English to an operations manager.
- Name the specific agent and step
- Say what decision was made and WHY
- If retried, explain the retry logic
- If escalated, say exactly what the human needs to do
- End with one clear recommendation
- Keep it under 150 words."""

# Ensure root is in sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.append(str(root))

from shared.db import get_connection

def get_traces_for_workflow(workflow_id: str) -> list:
    """
    Fetches all traces for a workflow_id from DB.
    """
    try:
        conn = get_connection()
        rows = conn.execute("""
            SELECT * FROM traces
            WHERE workflow_id = ?
            ORDER BY created_at ASC
        """, (workflow_id,)).fetchall()
        conn.close()
        return [dict(r) for r in rows]
    except Exception as e:
        print(f"[explainer] Could not fetch traces from DB: {e}")
        return []


def explain_decision(workflow_id: str, question: str, traces: list = None) -> str:
    """
    Takes workflow traces (list of dicts) and a question.
    Returns a plain-English explanation string.
    """
    if not traces:
        traces = get_traces_for_workflow(workflow_id)

    if not traces:
        return f"No traces found for workflow '{workflow_id}'."

    traces_json = json.dumps(traces, indent=2, default=str)

    prompt = f"""Here are the execution traces for workflow '{workflow_id}':

{traces_json}

The manager asks: {question}

Answer in plain English. Reference specific agents and steps from the traces.
End with a clear recommendation."""

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
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ]
            },
            timeout=30
        )

        result = response.json()

        if "error" in result:
            return f"Explainer error: {result['error'].get('message', 'unknown error')}"

        return result["choices"][0]["message"]["content"].strip()

    except httpx.TimeoutException:
        return "Explanation timed out. Please try again."
    except Exception as e:
        return f"Explainer failed: {str(e)}"