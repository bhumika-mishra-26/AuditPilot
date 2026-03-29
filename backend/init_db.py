<<<<<<< HEAD
from sqlmodel import SQLModel, Session, select, func
from shared.db import engine
from shared.models import PatternMemory, Trace, Client, PurchaseOrder, Task, SystemicAlert, BriefingLog, Workflow, Vendor
=======
"""
init_db.py

AuditPilot — Database initialisation script.
Run this ONCE before starting the project.
"""

import os
import json
>>>>>>> upstream/main
from datetime import datetime
import json
import os

<<<<<<< HEAD
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
=======
from shared.db import get_connection, TURSO_URL
import sqlite3  # for type hinting


def create_tables(conn: sqlite3.Connection) -> None:
    statements = [
        """CREATE TABLE IF NOT EXISTS pattern_memory (
            error_hash          TEXT PRIMARY KEY,
            error_type          TEXT NOT NULL,
            agent               TEXT NOT NULL,
            recommended_action  TEXT NOT NULL,
            attempts            INTEGER NOT NULL DEFAULT 0,
            successes           INTEGER NOT NULL DEFAULT 0,
            success_rate        REAL NOT NULL DEFAULT 0.0,
            last_seen_at        TEXT NOT NULL,
            context             TEXT,
            systemic_flag       INTEGER NOT NULL DEFAULT 0,
            last_systemic_at    TEXT
        )""",
        """CREATE TABLE IF NOT EXISTS traces (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            workflow_id     TEXT NOT NULL,
            workflow_type   TEXT NOT NULL,
            step_id         TEXT NOT NULL,
            agent           TEXT NOT NULL,
            input_data      TEXT,
            output_data     TEXT,
            status          TEXT NOT NULL,
            error_hash      TEXT,
            error_type      TEXT,
            decision        TEXT,
            decision_reason TEXT,
            log_message     TEXT,
            duration_ms     INTEGER,
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )""",
        """CREATE TABLE IF NOT EXISTS clients (
            client_id       TEXT PRIMARY KEY,
            name            TEXT NOT NULL,
            email           TEXT UNIQUE NOT NULL,
            phone           TEXT,
            gstin           TEXT,
            business_type   TEXT,
            onboarded_at    TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            status          TEXT NOT NULL DEFAULT 'active'
        )""",
        """CREATE TABLE IF NOT EXISTS purchase_orders (
            po_number       TEXT PRIMARY KEY,
            vendor_id       TEXT NOT NULL,
            vendor_name     TEXT NOT NULL,
            amount          REAL NOT NULL,
            invoice_amount  REAL,
            status          TEXT NOT NULL DEFAULT 'pending',
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )""",
        """CREATE TABLE IF NOT EXISTS tasks (
            task_id         TEXT PRIMARY KEY,
            workflow_id     TEXT NOT NULL,
            owner_id        TEXT,
            owner_name      TEXT,
            title           TEXT NOT NULL,
            deadline        TEXT,
            priority        TEXT DEFAULT 'medium',
            status          TEXT NOT NULL DEFAULT 'pending',
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )""",
        """CREATE TABLE IF NOT EXISTS systemic_alerts (
            id                  INTEGER PRIMARY KEY AUTOINCREMENT,
            error_hash          TEXT NOT NULL,
            error_type          TEXT NOT NULL,
            affected_workflows  TEXT NOT NULL,
            occurrence_count    INTEGER NOT NULL,
            context             TEXT,
            resolved            INTEGER NOT NULL DEFAULT 0,
            created_at          TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )""",
        """CREATE TABLE IF NOT EXISTS briefing_log (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            briefing_date   TEXT NOT NULL,
            items_count     INTEGER NOT NULL DEFAULT 0,
            email_sent      INTEGER NOT NULL DEFAULT 0,
            content         TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )""",
        """CREATE TABLE IF NOT EXISTS workflows (
            workflow_id     TEXT PRIMARY KEY,
            workflow_type   TEXT NOT NULL,
            status          TEXT NOT NULL,
            input_payload   TEXT,
            created_at      TEXT NOT NULL DEFAULT (datetime('now','localtime')),
            updated_at      TEXT NOT NULL DEFAULT (datetime('now','localtime'))
        )""",
    ]

    for stmt in statements:
        conn.execute(stmt)

    conn.commit()
    print("✅ Tables created")


def seed_pattern_memory(conn: sqlite3.Connection) -> None:
    rows = [
        ("hash_404_vendor", "HTTP_404_vendor_not_found", "execution_agent", "escalate", 20, 6, 0.30, "2024-03-14 09:23:00", "...", 0, None),
        ("hash_503_kyc", "HTTP_503_kyc_unavailable", "execution_agent", "retry", 15, 13, 0.87, "2024-03-14 11:45:00", "...", 0, None),
        ("hash_gstin_val", "GSTIN_format_invalid", "intake_agent", "escalate", 8, 0, 0.00, "2024-03-13 14:12:00", "...", 0, None),
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO pattern_memory VALUES (?,?,?,?,?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()


def seed_existing_clients(conn: sqlite3.Connection) -> None:
    rows = [
        ("C-001", "Mehta Textiles Pvt Ltd", "accounts@mehtatex.in", "9876543210", "27AAPFM0939F1ZV", "Textiles", "2024-01-10 09:00:00", "active"),
    ]

    conn.executemany(
        "INSERT OR IGNORE INTO clients VALUES (?,?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()


def seed_test_traces(conn: sqlite3.Connection) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    rows = [
        ("WF-MTG001", "W3", "T9", "intake_agent", json.dumps({"notes": "notes"}), json.dumps({"tasks": 2}), "success", None, None, None, None, "Validation passed", 150, now),
        ("WF-MTG001", "W3", "T10", "extraction_agent", json.dumps({"notes": "notes"}), json.dumps({"tasks": 2}), "success", None, None, None, None, "Extracted 2 tasks", 800, now),
    ]

    conn.executemany(
        """INSERT INTO traces (
            workflow_id, workflow_type, step_id, agent,
            input_data, output_data, status,
            error_hash, error_type, decision, decision_reason,
            log_message, duration_ms, created_at
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        rows,
    )
    conn.commit()


def verify(conn: sqlite3.Connection) -> None:
    tables = [
        "pattern_memory",
        "traces",
        "clients",
        "purchase_orders",
        "tasks",
        "systemic_alerts",
        "briefing_log",
        "workflows",
    ]

    for t in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"{t} → {count} rows")


def main() -> None:
    if not TURSO_URL:
        print("⚠️ Using local SQLite DB")

    conn = get_connection()

    create_tables(conn)
    seed_pattern_memory(conn)
    seed_existing_clients(conn)
    seed_test_traces(conn)
    verify(conn)

    conn.close()
>>>>>>> upstream/main


if __name__ == "__main__":
    if os.getenv("RUN_DB_INIT", "false").lower() == "true":
        print("🚀 Initializing database...")
        main()
    else:
        print("Skipping DB init. Set RUN_DB_INIT=true to run.")
