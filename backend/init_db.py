"""
init_db.py

AuditPilot — Database initialisation script.
Run this ONCE before starting the project.
"""

import sqlite3
import os
import json
from pathlib import Path
from datetime import datetime

DB_PATH = Path(__file__).resolve().parent / "auditpilot.db"

def get_connection() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

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
    print("  8 tables created.")

def seed_pattern_memory(conn: sqlite3.Connection) -> None:
    rows = [
        ("hash_404_vendor", "HTTP_404_vendor_not_found", "execution_agent", "escalate", 20, 6, 0.30, "2024-03-14 09:23:00", "...", 0, None),
        ("hash_503_kyc", "HTTP_503_kyc_unavailable", "execution_agent", "retry", 15, 13, 0.87, "2024-03-14 11:45:00", "...", 0, None),
        ("hash_gstin_val", "GSTIN_format_invalid", "intake_agent", "escalate", 8, 0, 0.00, "2024-03-13 14:12:00", "...", 0, None),
    ]
    conn.executemany("INSERT OR IGNORE INTO pattern_memory VALUES (?,?,?,?,?,?,?,?,?,?,?)", rows)
    conn.commit()

def seed_existing_clients(conn: sqlite3.Connection) -> None:
    rows = [
        ("C-001", "Mehta Textiles Pvt Ltd", "accounts@mehtatex.in", "9876543210", "27AAPFM0939F1ZV", "Textiles", "2024-01-10 09:00:00", "active"),
    ]
    conn.executemany("INSERT OR IGNORE INTO clients VALUES (?,?,?,?,?,?,?,?)", rows)
    conn.commit()

def seed_test_traces(conn: sqlite3.Connection) -> None:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = [
        ("WF-MTG001", "W3", "T9", "intake_agent", json.dumps({"notes": "notes"}), json.dumps({"tasks": 2}), "success", None, None, None, None, "Validation passed", 150, now),
        ("WF-MTG001", "W3", "T10", "extraction_agent", json.dumps({"notes": "notes"}), json.dumps({"tasks": 2}), "success", None, None, None, None, "Extracted 2 tasks", 800, now),
    ]
    conn.executemany("INSERT INTO traces (workflow_id, workflow_type, step_id, agent, input_data, output_data, status, error_hash, error_type, decision, decision_reason, log_message, duration_ms, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", rows)
    conn.commit()

def verify(conn: sqlite3.Connection) -> None:
    tables = ["pattern_memory", "traces", "clients", "purchase_orders", "tasks", "systemic_alerts", "briefing_log", "workflows"]
    for t in tables:
        count = conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        print(f"    {t:<22} → {count} rows")

def main() -> None:
    if DB_PATH.exists():
        DB_PATH.unlink()
    conn = get_connection()
    create_tables(conn)
    seed_pattern_memory(conn)
    seed_existing_clients(conn)
    seed_test_traces(conn)
    verify(conn)
    conn.close()

if __name__ == "__main__":
    main()