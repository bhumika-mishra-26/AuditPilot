from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from api.deps.db import get_db
import sqlite3
import json
import os
import urllib.request
from typing import AsyncGenerator

router = APIRouter()

class ExplainRequest(BaseModel):
    workflow_id: str
    question: str

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY", "")
MODEL = "openrouter/auto"
URL = "https://openrouter.ai/api/v1/chat/completions"

async def _stream_explanation(prompt: str) -> AsyncGenerator[str, None]:
    """
    Streams tokens from OpenRouter to the client.
    """
    payload = {
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "stream": True
    }
    
    req = urllib.request.Request(
        URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json"
        },
        method="POST"
    )

    # Use a dummy stream if no API key is present
    if not OPENROUTER_API_KEY:
        yield "OpenRouter API Key is missing. I cannot generate a real-time explanation without it. "
        yield "However, I can see the traces for this workflow in the database."
        return

    try:
        with urllib.request.urlopen(req) as response:
            for line in response:
                if line:
                    line_str = line.decode("utf-8")
                    if line_str.startswith("data: "):
                        content = line_str[6:].strip()
                        if content == "[DONE]":
                            break
                        try:
                            data = json.loads(content)
                            delta = data["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                yield delta
                        except json.JSONDecodeError:
                            continue
    except Exception as e:
        yield f"Error during streaming: {str(e)}"

@router.post("/explain")
async def explain_workflow(request: ExplainRequest, db: sqlite3.Connection = Depends(get_db)):
    """
    Explains a workflow's execution using its traces.
    Streams the response token by token.
    """
    # Fetch traces
    rows = db.execute(
        "SELECT agent, step_id, status, error_type, decision_reason FROM traces WHERE workflow_id = ?",
        (request.workflow_id,)
    ).fetchall()
    
    if not rows:
        raise HTTPException(status_code=404, detail="No traces found for this workflow.")

    traces_summary = json.dumps([dict(r) for r in rows], indent=2)
    
    prompt = f"""You are an audit assistant. Your job is to explain the execution of a business workflow to a user.
    
Here are the execution traces for workflow {request.workflow_id}:
{traces_summary}

User question: {request.question}

Explain in plain English what happened and why. Use the traces to justify your answer.
"""

    return StreamingResponse(_stream_explanation(prompt), media_type="text/event-stream")
