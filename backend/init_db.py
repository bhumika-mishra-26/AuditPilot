from sqlmodel import SQLModel, Session, select, func
from shared.db import engine
from shared.models import PatternMemory, Trace, Client, PurchaseOrder, Task, SystemicAlert, BriefingLog, Workflow, Vendor
from datetime import datetime
import json
import os

def create_tables() -> None:
    print("  Creating tables via SQLModel...")
    SQLModel.metadata.create_all(engine)
    print("  All tables created successfully.")

def seed_vendors() -> None:
    path = os.path.join(os.path.dirname(__file__), "data", "vendors.json")
    if not os.path.exists(path):
        print(f"  [WARN] vendors.json not found at {path}")
        return

    try:
        with open(path, "r") as f:
            data = json.load(f)
        
        with Session(engine) as session:
            for item in data:
                vendor = Vendor(
                    vendor_id=item.get("vendor_id"),
                    name=item.get("name"),
                    gstin=item.get("gstin"),
                    status=item.get("status", "active"),
                    risk=item.get("risk", "Low"),
                    spend=item.get("spend", "$0"),
                    purpose=item.get("purpose")
                )
                session.merge(vendor)
            session.commit()
            print(f"  Seeded {len(data)} vendors from JSON.")
    except Exception as e:
        print(f"  [ERROR] Failed to seed vendors: {e}")

def seed_pattern_memory() -> None:
    with Session(engine) as session:
        patterns = [
            PatternMemory(
                error_hash="hash_404_vendor",
                error_type="HTTP_404_vendor_not_found",
                agent="execution_agent",
                recommended_action="escalate",
                attempts=20,
                successes=6,
                success_rate=0.30,
                last_seen_at="2024-03-14 09:23:00",
                context="...",
                systemic_flag=0
            ),
            PatternMemory(
                error_hash="hash_503_kyc",
                error_type="HTTP_503_kyc_unavailable",
                agent="execution_agent",
                recommended_action="retry",
                attempts=15,
                successes=13,
                success_rate=0.87,
                last_seen_at="2024-03-14 11:45:00",
                context="...",
                systemic_flag=0
            ),
            PatternMemory(
                error_hash="hash_gstin_val",
                error_type="GSTIN_format_invalid",
                agent="intake_agent",
                recommended_action="escalate",
                attempts=8,
                successes=0,
                success_rate=0.00,
                last_seen_at="2024-03-13 14:12:00",
                context="...",
                systemic_flag=0
            )
        ]
        for p in patterns:
            session.merge(p)
        session.commit()
        print("  Pattern memory seeded.")

def seed_existing_clients() -> None:
    with Session(engine) as session:
        client = Client(
            client_id="C-001",
            name="Mehta Textiles Pvt Ltd",
            email="accounts@mehtatex.in",
            phone="9876543210",
            gstin="27AAPFM0939F1ZV",
            business_type="Textiles",
            onboarded_at="2024-01-10 09:00:00",
            status="active"
        )
        session.merge(client)
        session.commit()
        print("  Existing clients seeded.")

def seed_test_traces() -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with Session(engine) as session:
        traces = [
            Trace(
                workflow_id="WF-MTG001",
                workflow_type="W3",
                step_id="T9",
                agent="intake_agent",
                input_data=json.dumps({"notes": "notes"}),
                output_data=json.dumps({"tasks": 2}),
                status="success",
                log_message="Validation passed",
                duration_ms=150,
                created_at=now
            ),
            Trace(
                workflow_id="WF-MTG001",
                workflow_type="W3",
                step_id="T10",
                agent="extraction_agent",
                input_data=json.dumps({"notes": "notes"}),
                output_data=json.dumps({"tasks": 2}),
                status="success",
                log_message="Extracted 2 tasks",
                duration_ms=800,
                created_at=now
            )
        ]
        for t in traces:
            session.add(t)
        session.commit()
        print("  Test traces seeded.")

def verify() -> None:
    print("\n  Verifying table counts:")
    with Session(engine) as session:
        tables = [PatternMemory, Trace, Client, PurchaseOrder, Task, SystemicAlert, BriefingLog, Workflow, Vendor]
        for table in tables:
            try:
                count = session.exec(select(func.count()).select_from(table)).one()
                print(f"    {table.__tablename__:<22} → {count} rows")
            except Exception as e:
                print(f"    {table.__tablename__:<22} → ERROR: {e}")

def main() -> None:
    create_tables()
    seed_vendors()
    seed_pattern_memory()
    seed_existing_clients()
    seed_test_traces()
    verify()

if __name__ == "__main__":
    main()