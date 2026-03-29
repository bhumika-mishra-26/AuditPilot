from sqlmodel import SQLModel, create_engine, Session, select
import os
from pathlib import Path
from dotenv import load_dotenv
import json
from datetime import datetime
from .models import PatternMemory, Trace, Client, PurchaseOrder, Task, SystemicAlert, BriefingLog, Workflow

load_dotenv()

# Neon or local SQLite/Postgres URL
DATABASE_URL = os.environ.get("DATABASE_URL", "sqlite:///auditpilot.db")

# SSL configuration for Neon (required)
connect_args = {}
if "sqlite" not in DATABASE_URL:
    connect_args = {"sslmode": "require"}

engine = create_engine(DATABASE_URL, connect_args=connect_args)

from sqlalchemy.orm import sessionmaker
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine, class_=Session)

def get_session():
    """Provides a SQLModel session."""
    with Session(engine) as session:
        yield session

def get_connection():
    """
    Backward compatibility for raw SQL calls.
    Note: Returns a SQLAlchemy connection object.
    It's recommended to use get_session() and SQLModel classes instead.
    """
    return engine.connect()

def write_trace(
    workflow_id: str,
    workflow_type: str,
    step_id: str,
    agent: str,
    status: str,
    input_data: dict = None,
    output_data: dict = None,
    error_hash: str = None,
    error_type: str = None,
    decision: str = None,
    decision_reason: str = None,
    log_message: str = None,
    duration_ms: int = None,
):
    with Session(engine) as session:
        trace = Trace(
            workflow_id=workflow_id,
            workflow_type=workflow_type,
            step_id=step_id,
            agent=agent,
            status=status,
            input_data=json.dumps(input_data) if input_data else None,
            output_data=json.dumps(output_data) if output_data else None,
            error_hash=error_hash,
            error_type=error_type,
            decision=decision,
            decision_reason=decision_reason,
            log_message=log_message,
            duration_ms=duration_ms
        )
        session.add(trace)
        session.commit()

def read_pattern(error_hash: str) -> dict | None:
    with Session(engine) as session:
        statement = select(PatternMemory).where(PatternMemory.error_hash == error_hash)
        pattern = session.exec(statement).first()
        return pattern.model_dump() if pattern else None

def update_pattern(error_hash: str, retry_succeeded: bool):
    with Session(engine) as session:
        statement = select(PatternMemory).where(PatternMemory.error_hash == error_hash)
        pattern = session.exec(statement).first()
        if not pattern:
            return

        pattern.attempts += 1
        pattern.successes += 1 if retry_succeeded else 0
        pattern.success_rate = pattern.successes / pattern.attempts
        pattern.last_seen_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        session.add(pattern)
        session.commit()

def count_affected_workflows(error_hash: str) -> tuple[int, list[str]]:
    with Session(engine) as session:
        statement = select(Trace.workflow_id).where(
            Trace.error_hash == error_hash,
            Trace.status.in_(["failed", "escalated"])
        ).distinct()
        results = session.exec(statement).all()
        return len(results), list(results)

def write_systemic_alert(
    error_hash: str,
    error_type: str,
    affected_workflows: list[str],
    context: str = None,
):
    with Session(engine) as session:
        alert = SystemicAlert(
            error_hash=error_hash,
            error_type=error_type,
            affected_workflows=json.dumps(affected_workflows),
            occurrence_count=len(affected_workflows),
            context=context
        )
        session.add(alert)
        session.commit()

def get_workflow_tasks(workflow_id: str) -> list[dict]:
    with Session(engine) as session:
        statement = select(Task).where(Task.workflow_id == workflow_id).order_by(Task.created_at)
        tasks = session.exec(statement).all()
        return [t.model_dump() for t in tasks]

def get_systemic_alerts() -> list[dict]:
    with Session(engine) as session:
        statement = select(SystemicAlert).where(SystemicAlert.resolved == 0).order_by(SystemicAlert.created_at.desc())
        alerts = session.exec(statement).all()
        return [a.model_dump() for a in alerts]

def get_briefing_history(limit: int = 10) -> list[dict]:
    with Session(engine) as session:
        statement = select(BriefingLog).order_by(BriefingLog.created_at.desc()).limit(limit)
        briefings = session.exec(statement).all()
        return [b.model_dump() for b in briefings]

def get_all_traces(limit: int = 100) -> list[dict]:
    with Session(engine) as session:
        statement = select(Trace).order_by(Trace.created_at.desc()).limit(limit)
        traces = session.exec(statement).all()
        return [t.model_dump() for t in traces]

def get_workflow_traces(workflow_id: str) -> list[dict]:
    with Session(engine) as session:
        statement = select(Trace).where(Trace.workflow_id == workflow_id).order_by(Trace.created_at)
        traces = session.exec(statement).all()
        return [t.model_dump() for t in traces]

def update_workflow_input(workflow_id: str, input_payload: dict):
    with Session(engine) as session:
        statement = select(Workflow).where(Workflow.workflow_id == workflow_id)
        wf = session.exec(statement).first()
        if wf:
            wf.input_payload = json.dumps(input_payload)
            wf.updated_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            session.add(wf)
            session.commit()