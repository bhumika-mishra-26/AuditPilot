from sqlmodel import SQLModel, Field
from typing import Optional, List
from datetime import datetime
import json

class PatternMemory(SQLModel, table=True):
    __tablename__ = "pattern_memory"
    error_hash: str = Field(primary_key=True)
    error_type: str
    agent: str
    recommended_action: str
    attempts: int = Field(default=0)
    successes: int = Field(default=0)
    success_rate: float = Field(default=0.0)
    last_seen_at: str
    context: Optional[str] = None
    systemic_flag: int = Field(default=0)
    last_systemic_at: Optional[str] = None

class Trace(SQLModel, table=True):
    __tablename__ = "traces"
    id: Optional[int] = Field(default=None, primary_key=True)
    workflow_id: str
    workflow_type: str
    step_id: str
    agent: str
    input_data: Optional[str] = None # JSON string
    output_data: Optional[str] = None # JSON string
    status: str
    error_hash: Optional[str] = None
    error_type: Optional[str] = None
    decision: Optional[str] = None
    decision_reason: Optional[str] = None
    log_message: Optional[str] = None
    duration_ms: Optional[int] = None
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class Client(SQLModel, table=True):
    __tablename__ = "clients"
    client_id: str = Field(primary_key=True)
    name: str
    email: str = Field(unique=True)
    phone: Optional[str] = None
    gstin: Optional[str] = None
    business_type: Optional[str] = None
    onboarded_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    status: str = Field(default="active")

class PurchaseOrder(SQLModel, table=True):
    __tablename__ = "purchase_orders"
    po_number: str = Field(primary_key=True)
    vendor_id: str
    vendor_name: str
    amount: float
    invoice_amount: Optional[float] = None
    status: str = Field(default="pending")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class Task(SQLModel, table=True):
    __tablename__ = "tasks"
    task_id: str = Field(primary_key=True)
    workflow_id: str
    owner_id: Optional[str] = None
    owner_name: Optional[str] = None
    title: str
    deadline: Optional[str] = None
    priority: str = Field(default="medium")
    status: str = Field(default="pending")
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class SystemicAlert(SQLModel, table=True):
    __tablename__ = "systemic_alerts"
    id: Optional[int] = Field(default=None, primary_key=True)
    error_hash: str
    error_type: str
    affected_workflows: str # JSON list string
    occurrence_count: int
    context: Optional[str] = None
    resolved: int = Field(default=0)
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class BriefingLog(SQLModel, table=True):
    __tablename__ = "briefing_log"
    id: Optional[int] = Field(default=None, primary_key=True)
    briefing_date: str
    items_count: int = Field(default=0)
    email_sent: int = Field(default=0)
    content: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class Workflow(SQLModel, table=True):
    __tablename__ = "workflows"
    workflow_id: str = Field(primary_key=True)
    workflow_type: str
    status: str
    input_payload: Optional[str] = None # JSON string
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    updated_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

class Vendor(SQLModel, table=True):
    __tablename__ = "vendors"
    vendor_id: str = Field(primary_key=True)
    name: str
    gstin: Optional[str] = None
    status: str = Field(default="active")
    risk: Optional[str] = Field(default="Low")
    spend: Optional[str] = Field(default="$0")
    purpose: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
