from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from modules.scheduler import run_briefing_job
from shared.db import get_briefing_history

router = APIRouter()

class BriefingResponse(BaseModel):
    briefing_text: str
    workflow_count: int
    needs_action_count: int
    generated_at: str
    email_status: str
    email_to: str = ""
    email_reason: str = ""

class BriefingRequest(BaseModel):
    recipient_email: str = None

@router.post("/generate", response_model=BriefingResponse)
async def trigger_briefing(request: BriefingRequest = None):
    """Manual trigger for the briefing job."""
    try:
        email = request.recipient_email if request else None
        result = run_briefing_job(recipient_email=email)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/history")
async def get_history(limit: int = 10):
    """Returns the history of generated briefings."""
    try:
        history = get_briefing_history(limit)
        return {"history": history}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
