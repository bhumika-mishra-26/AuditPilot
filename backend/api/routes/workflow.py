from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from sqlmodel import Session, select, func
from api.deps.db import get_db
from shared.models import Workflow, Trace, PatternMemory
import uuid
import json
from datetime import datetime
from orchestrator.graph import graph as orchestrator_graph
from shared.logger import log

router = APIRouter()

class RunRequest(BaseModel):
    workflow_type: str
    input_payload: Dict[str, Any]

class WorkflowResponse(BaseModel):
    workflow_id: str
    status: str

class StartRequest(BaseModel):
    prompt: str

def _classify_task(user_task: str) -> dict:
    import re
    task_lower = user_task.lower()
    w1_keywords = ["onboard", "register", "add client", "new client", "sign up", "enroll", "create account", "kyc"]
    w2_keywords = ["pay", "payment", "purchase order", "po", "invoice", "vendor", "procurement", "approve", "transaction", "pay to", "process payment", "settle"]
    w3_keywords = ["meeting", "notes", "assign task", "action item", "action items", "extract task", "tasks", "transcript", "minute", "discussed", "follow up", "sprint", "standup", "sync"]
    
    w1_score = sum(1 for k in w1_keywords if k in task_lower)
    w2_score = sum(1 for k in w2_keywords if k in task_lower)
    w3_score = sum(1 for k in w3_keywords if k in task_lower)
    total = w1_score + w2_score + w3_score
    
    if total == 0: return {"route": "unclear", "confidence": 0.0}
    
    scores = {"W1": w1_score, "W2": w2_score, "W3": w3_score}
    
    # If tie, default to W3 because W3 is the safest fallback if there are multiple action items mentioned.
    if w3_score >= max(w1_score, w2_score) and w3_score > 0:
        best = "W3"
    else:
        best = max(scores, key=scores.get)
    
    extracted = {}
    words = user_task.split()
    for i, w in enumerate(words):
        if w.lower() in ("onboard", "register", "pay") and i + 1 < len(words):
            extracted["name"] = " ".join(words[i+1:i+3])
    
    amounts = re.findall(r'\b\d[\d,]*\b', user_task)
    if amounts: extracted["amount"] = amounts[-1].replace(",", "")
    
    # For W3 (meeting), use the entire prompt as notes
    if best == "W3":
        extracted["notes"] = user_task
    
    route_map = {"W1": "onboarding", "W2": "procurement", "W3": "meeting"}
    return {"type": route_map[best], "confidence": round(scores[best]/total, 2), "params": extracted}

# ── 2.1: POST /run ───────────────────────────────────────

def _execute_workflow_task(workflow_id: str, workflow_type: str, input_payload: Dict[str, Any]):
    print(f"\n[DEBUG] [EXECUTOR] Starting execution for {workflow_id} ({workflow_type})\n")
    from shared.db import SessionLocal
    
    with SessionLocal() as session:
        # Safety Check: Don't run if already completed or failed
        statement = select(Workflow).where(Workflow.workflow_id == workflow_id)
        current = session.exec(statement).first()
        if current and current.status in ("completed", "failed"):
            print(f"[DEBUG] [EXECUTOR] Skipping {workflow_id} - already {current.status}")
            return
    
    # Map friendly type to orchestrator route (bypass LLM classification for API runs)
    workflow_route_map = {
        "onboarding": "W1",
        "procurement": "W2",
        "meeting": "W3",
    }

    # Map friendly type to user_task for logs (not for routing)
    type_map = {
        "onboarding": f"onboard {input_payload.get('name', input_payload.get('client_name', 'new client'))}",
        "procurement": f"process payment for {input_payload.get('po_no', input_payload.get('po_number', 'PO'))}",
        "meeting": "assign tasks from meeting notes",
    }
    
    if "original_prompt" in input_payload:
        user_task = input_payload["original_prompt"]
    else:
        user_task = type_map.get(workflow_type, "run workflow")
    
    human_res = input_payload.get("human_resolution")
    if human_res:
        user_task += f" — Note from user: {human_res}"
    
    bypass_llm = bool(input_payload.get("__bypass_llm"))

    initial_state = {
        "user_task": user_task,
        "extracted_params": input_payload,
        "logs": [log("API", f"Async execution started for {workflow_id}")],
        "workflow_results": [],
        "error": None,
        "workflow_id": workflow_id,
        "is_api_run": True,
        # Pass human_resolution directly into LangGraph state so all nodes
        # (especially owner_resolution_node) can read it without parsing user_task.
        "human_resolution": human_res or "",
    }

    # Only bypass the LLM router on RESUME runs (when we already have a complete payload).
    # For fresh `/start` runs, keep the LLM so it can extract fields like vendor_id/po_no/notes.
    if bypass_llm:
        initial_state["route"] = workflow_route_map.get(workflow_type, "unclear")
        initial_state["task_list"] = [{
            "route": workflow_route_map.get(workflow_type, "unclear"),
            "extracted_params": input_payload,
        }]

    try:
        # Run orchestrator
        final_state = orchestrator_graph.invoke(initial_state)
        # Check if any step is 'escalated'
        is_escalated = any(
            log_entry.get("status") in ("escalated", "pending_review")
            for log_entry in final_state.get("workflow_results", [])
        )

        if is_escalated:
            status = "escalated"
        else:
            results = final_state.get("workflow_results", [])
            any_failure = any(r.get("status") == "failed" for r in results)
            
            if final_state.get("error") or any_failure:
                status = "failed"
            else:
                status = "completed"
        
        if current:
            current.status = status
            current.updated_at = datetime.now()
            session.add(current)
            session.commit()
    except Exception as e:
        if current:
            current.status = "failed"
            current.updated_at = datetime.now()
            session.add(current)
            session.commit()

@router.post("/run", response_model=WorkflowResponse)
async def run_workflow(request: RunRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Kicks off a workflow asynchronously. 
    Returns the workflow_id immediately.
    """
    valid_types = ["onboarding", "procurement", "meeting"]
    if request.workflow_type not in valid_types:
        raise HTTPException(status_code=400, detail=f"Invalid workflow type. Must be one of {valid_types}")

    workflow_id = str(uuid.uuid4())
    
    try:
        # Register in DB
        new_workflow = Workflow(
            workflow_id=workflow_id,
            workflow_type=request.workflow_type,
            status="running",
            input_payload=json.dumps(request.input_payload)
        )
        db.add(new_workflow)
        db.commit()

        background_tasks.add_task(_execute_workflow_task, workflow_id, request.workflow_type, request.input_payload)

        return {"workflow_id": workflow_id, "status": "running"}
    except Exception as e:
        import traceback
        error_msg = f"Crash in run_workflow: {str(e)}\n{traceback.format_exc()}"
        print(error_msg)
        raise HTTPException(status_code=500, detail=error_msg)

@router.post("/start")
async def start_workflow_nl(request: StartRequest, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Classifies natural language prompt and starts the appropriate workflow.
    """
    classification = _classify_task(request.prompt)
    if classification["route" if "route" in classification else "type"] == "unclear":
        # Fallback to some default or error
        classification = {"type": "onboarding", "params": {"name": "Unknown Entity"}}
        
    workflow_type = classification["type"]
    input_payload = classification["params"]
    # Preserve the raw prompt so the LLM intent classifier can extract all details (e.g., email)
    input_payload["original_prompt"] = request.prompt
    
    # For W3 (meeting), ensure notes is always set from the prompt.
    if workflow_type == "meeting" and not input_payload.get("notes"):
        input_payload["notes"] = request.prompt
    
    workflow_id = str(uuid.uuid4())
    new_workflow = Workflow(
        workflow_id=workflow_id,
        workflow_type=workflow_type,
        status="running",
        input_payload=json.dumps(input_payload)
    )
    db.add(new_workflow)
    db.commit()
    
    background_tasks.add_task(_execute_workflow_task, workflow_id, workflow_type, input_payload)
    return {"workflow_id": workflow_id, "workflow_type": workflow_type, "status": "running"}

@router.get("/list")
async def list_workflows(limit: int = 20, db: Session = Depends(get_db)):
    """
    Returns a list of the most recent workflows from the workflows table.
    """
    statement = select(Workflow).order_by(Workflow.created_at.desc()).limit(limit)
    results = db.exec(statement).all()
    return [r.model_dump() for r in results]

# ── 2.2: GET /status and /graph ──────────────────────────

@router.get("/status/{workflow_id}")
async def get_workflow_status(workflow_id: str, db: Session = Depends(get_db)):
    """
    Returns the status of all steps for a specific workflow_id.
    """
    statement = select(Trace).where(Trace.workflow_id == workflow_id).order_by(Trace.created_at.asc())
    results = db.exec(statement).all()
    
    scalar_rows = []
    for r in results:
        row = r.model_dump()
        for f in ["input_data", "output_data"]:
            if row.get(f) and isinstance(row[f], str):
                try:
                    row[f] = json.loads(row[f])
                except json.JSONDecodeError:
                    row[f] = {}
        scalar_rows.append(row)
    
    workflow_stmt = select(Workflow).where(Workflow.workflow_id == workflow_id)
    workflow = db.exec(workflow_stmt).first()
    
    workflow_logs = []
    for r in scalar_rows:
        workflow_logs.append({
            "timestamp": r.get("created_at"),
            "agent": r.get("agent"),
            "message": r.get("log_message") if r.get("log_message") else (r.get("decision_reason") if r.get("decision_reason") else r.get("status"))
        })
    
    # Fetch patterns for memory panel
    patterns_stmt = select(PatternMemory).limit(5)
    patterns = db.exec(patterns_stmt).all()

    # ... error_map remains the same ...
    error_map = {
        "EMAIL_MISSING": {
            "reason": "Please provide the missing client email address.",
            "options": ["submit_email", "cancel_onboarding"]
        },
        "NAME_MISSING": {
            "reason": "Please provide the missing client name.",
            "options": ["submit_name", "cancel_onboarding"]
        },
        "GSTIN_format_invalid": {
            "reason": "The GSTIN provided is invalid. Please type the correct 15-character GSTIN in the box below, or skip if the client does not have one.",
            "options": ["skip_gstin", "cancel_onboarding"]
        },
        "DUPLICATE_CLIENT": {
            "reason": "This client already exists. Please confirm if you want to merge or cancel.",
            "options": ["merge_duplicate", "create_new_client", "cancel_onboarding"]
        },
        "HUMAN_REJECTED_ACTION": {
            "reason": "Account creation requires manual approval.",
            "options": ["approve_account", "reject_account"]
        },
        "HTTP_503_kyc_unavailable": {
            "reason": "KYC system is down. Do you want to retry or override?",
            "options": ["retry_kyc", "manual_docs_upload", "override_kyc"]
        },
        "HTTP_404_vendor_not_found": {
            "reason": "Vendor not found in system. Please onboard the vendor or choose to continue manually.",
            "options": ["onboard_vendor", "1 (continue)", "2 (cancel)"]
        },
        "HTTP_300_ambiguous_owner": {
            "reason": "Multiple team members match the owner name. Please select one.",
            "options": ["1", "2", "3", "cancel"]
        },
        "HTTP_404_owner_not_found": {
            "reason": "Task owner not found in team. You can add them as a new member, reassign, or skip.",
            "options": ["onboard_member", "reassign_to_me", "skip_task", "cancel"]
        },
        "INTAKE_NOTES_INVALID": {
            "reason": "Meeting notes are too short or invalid. Please provide more detail.",
            "options": ["retry", "cancel"]
        }
    }
    
    hitl_reason = None
    hitl_options = []
    
    latest_escalated = None
    for r in reversed(scalar_rows):
        if r.get("status") == "escalated" and r.get("error_type"):
            latest_escalated = r
            break
    if not latest_escalated:
        for r in reversed(scalar_rows):
            if r.get("status") == "escalated":
                latest_escalated = r
                break

    if latest_escalated and workflow and workflow.status == "escalated":
        latest_error_type = latest_escalated.get("error_type")
        if latest_error_type and latest_error_type in error_map:
            hitl_reason = error_map[latest_error_type]["reason"]
            hitl_options = error_map[latest_error_type]["options"]
            
            if latest_error_type == "HTTP_404_vendor_not_found":
                input_data = latest_escalated.get("input_data", {})
                v_id = input_data.get("vendor_id", "Unknown")
                hitl_reason = f"Vendor {v_id} not found in system. Please onboard or continue manually."
            
            if latest_error_type == "HTTP_300_ambiguous_owner":
                output_data = latest_escalated.get("output_data", {})
                opts = output_data.get("options", [])
                if opts:
                    hitl_reason = "Multiple team members match the owner name. Please select one."
                    hitl_options = opts + ["cancel"]
        else:
            hitl_reason = latest_escalated.get("decision_reason") or "Human intervention required to proceed."
            hitl_options = ["1 (continue)", "2 (cancel)"]
    else:
        last_error_type = None
        for r in reversed(scalar_rows):
            if r.get("error_type"):
                last_error_type = r["error_type"]
                break
        if last_error_type and last_error_type in error_map:
            hitl_reason = error_map[last_error_type]["reason"]
            hitl_options = error_map[last_error_type]["options"]

    summary = None
    for r in reversed(scalar_rows):
        if r.get("step_id") == "result_summary":
            output_data = r.get("output_data", {})
            if isinstance(output_data, str):
                try:
                    output_data = json.loads(output_data)
                except:
                    pass
            summary = output_data.get("final_reply")
            break

    return {
        "workflow_id": workflow_id,
        "state": workflow.status if workflow else "unknown",
        "type": workflow.workflow_type if workflow else "unknown",
        "steps": scalar_rows,
        "patterns": [p.model_dump() for p in patterns],
        "hitl_reason": hitl_reason,
        "hitl_options": hitl_options,
        "logs": workflow_logs,
        "summary": summary
    }

@router.get("/graph/{workflow_id}")
async def get_workflow_graph(workflow_id: str, db: Session = Depends(get_db)):
    """
    Returns nodes and edges for ReactFlow visualization.
    """
    statement = select(Trace.step_id, Trace.agent, Trace.status).where(Trace.workflow_id == workflow_id).order_by(Trace.created_at.asc())
    results = db.exec(statement).all()
    
    nodes = []
    edges = []
    
    # Simple linear layout for the graph based on traces
    for i, row in enumerate(results):
        nodes.append({
            "id": row[0],
            "data": {"label": f"{row[1]} ({row[0]})"},
            "status": row[2],
            "position": {"x": 250, "y": i * 100}
        })
        if i > 0:
            edges.append({
                "id": f"e{i-1}-{i}",
                "source": results[i-1][0],
                "target": row[0]
            })
            
    return {"nodes": nodes, "edges": edges}

# ── 2.6: POST /resume ────────────────────────────────────

class ResumeRequest(BaseModel):
    input: str = ""
    human_resolution: str = ""

@router.post("/resume/{workflow_id}")
async def resume_workflow(workflow_id: str, payload: ResumeRequest, background_tasks: BackgroundTasks, step_id: Optional[str] = None, db: Session = Depends(get_db)):
    """
    Resumes an escalated workflow.
    """
    if not step_id:
        stmt = select(Trace.step_id).where(Trace.workflow_id == workflow_id, Trace.status == "escalated").order_by(Trace.created_at.desc())
        step_id = db.exec(stmt).first()
        if not step_id:
            raise HTTPException(status_code=400, detail="No escalated step found to resume")

    # Fetch error type
    error_stmt = select(Trace.error_type).where(Trace.workflow_id == workflow_id, Trace.status == "escalated").order_by(Trace.created_at.desc())
    expected_error = db.exec(error_stmt).first()

    # Clear stale escalations
    traces_to_update = db.exec(select(Trace).where(Trace.workflow_id == workflow_id, Trace.status == "escalated")).all()
    for t in traces_to_update:
        t.status = "pending"
        db.add(t)

    # Update workflow status
    workflow = db.exec(select(Workflow).where(Workflow.workflow_id == workflow_id)).first()
    if not workflow:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    workflow.status = "running"
    workflow.updated_at = datetime.now()
    db.add(workflow)
    db.commit()
    
    input_data = json.loads(workflow.input_payload)
    input_data["__bypass_llm"] = True
    if payload.input or payload.human_resolution:
        raw = (payload.input or payload.human_resolution).strip()
        input_data["human_resolution"] = raw

        ACTION_KEYWORDS = (
            "submit_email", "submit_name", "correct", 
            "approve_account", "reject_account", "merge_duplicate", 
            "create_new_client", "retry_kyc", "override_kyc", 
            "manual_docs_upload", "cancel_onboarding",
            "onboard_vendor", "onboard_member",
            "reassign_to_me", "skip_task", "skip_gstin",
            "1", "2", "3", "continue", "reject", "approve", "cancel"
        )

        looks_like_email = ("@" in raw) and ("." in raw) and (" " not in raw) and (len(raw) <= 320)
        looks_like_gstin = (len(raw) == 15) and raw.isalnum()

        if looks_like_email and expected_error == "EMAIL_MISSING":
            input_data["email"] = raw
        elif looks_like_gstin and expected_error == "GSTIN_format_invalid":
            input_data["gstin"] = raw
        elif raw and raw.lower() not in ACTION_KEYWORDS:
            if expected_error == "NAME_MISSING" and len(raw) <= 120:
                input_data["name"] = raw
                input_data["client_name"] = raw

        workflow.input_payload = json.dumps(input_data)
        db.add(workflow)
        db.commit()
        
    background_tasks.add_task(_execute_workflow_task, workflow_id, workflow.workflow_type, input_data)
    return {"message": "Workflow resumed", "workflow_id": workflow_id}
