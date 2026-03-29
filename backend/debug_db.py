import sqlite3
import os
import json

DB_PATH = "auditpilot.db"

def test():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    row = conn.execute("SELECT step_id, agent, status, created_at, error_type, decision_reason, log_message FROM traces LIMIT 1").fetchone()
    if row:
        print(f"Row keys: {row.keys()}")
        d = dict(row)
        print(f"Dict keys: {d.keys()}")
        print(f"Log message: {d.get('log_message')}")
    else:
        print("No traces found")
    conn.close()

if __name__ == "__main__":
    test()
