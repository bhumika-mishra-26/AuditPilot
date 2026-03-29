"""
main.py

AuditPilot — Master entry point.

Two modes:
  1. Interactive mode (default) — type task in plain English
  2. Demo mode (--demo flag)    — runs all hardcoded test cases

Usage:
  python main.py          → interactive mode
  python main.py --demo   → demo mode
"""

import re
import sys
import json
import uuid
import shutil
from pathlib import Path

from shared.logger import log, log_section, log_step
from shared.error_map import get_error_hash
from orchestrator.graph import graph as orchestrator_graph
from shared.utils import classify_task_keywords

BASE = Path(__file__).resolve().parent

# ─────────────────────────────────────────────────────────
# INTERACTIVE MODE
# ─────────────────────────────────────────────────────────

def run_interactive():
    print(log_section("AuditPilot — Natural Language Mode"))
    print("  Type your task in plain English.")
    print("  Wait for the Orchestrator to process your request.")
    print("  Type 'exit' to quit.\n")

    while True:
        user_task = input("  You: ").strip()

        if not user_task:
            continue

        if user_task.lower() in ("exit", "quit", "q"):
            print("\n  Session ended.\n")
            _print_db_summary()
            break

        print()
        
        # Prepare state for the orchestrator
        initial_state = {
            "user_task": user_task,
            "logs": [log("CLI", f"Interactive request: {user_task}")],
            "workflow_results": [],
            "workflow_id": f"CLI-{str(uuid.uuid4())[:6].upper()}"
        }

        # Run the master orchestrator
        final_state = orchestrator_graph.invoke(initial_state)

        # Print orchestrator logs
        for entry in final_state.get("logs", []):
            print(f"  {entry}")
        
        # If the orchestrator needs clarification (e.g. low confidence)
        if final_state.get("needs_clarification"):
            print(f"\n  [Orchestrator] {final_state['clarification_question']}")
            answer = input("  Response: ").strip()
            if answer:
                initial_state["clarification_answer"] = answer
                final_state = orchestrator_graph.invoke(initial_state)
                for entry in final_state.get("logs", []):
                    print(f"  {entry}")

        print()
        again = input("  Run another task? (y/n): ").strip().lower()
        if again != "y":
            print("\n  Session ended.\n")
            _print_db_summary()
            break
        print()


# ─────────────────────────────────────────────────────────
# DEMO MODE
# ─────────────────────────────────────────────────────────

def run_demo():
    print(log_section("AuditPilot — Demo Mode"))

    # ── W1 ────────────────────────────────────────────────
    print(log_section("W1 — Client Onboarding"))

    seed   = BASE / "data" / "existing_clients.json"
    backup = BASE / "data" / "existing_clients.backup.json"
    shutil.copyfile(seed, backup)

    try:
        with open(BASE / "data" / "clients.json", "r", encoding="utf-8") as f:
            clients_raw = json.load(f)

        clients_data = []
        for c in clients_raw:
            client = dict(c)
            if "id" in client and "client_id" not in client:
                client["client_id"] = client["id"]
            clients_data.append(client)

        sequence      = ["C-001", "C-003", "C-005"]
        clients_by_id = {c["client_id"]: c for c in clients_data}

        for cid in sequence:
            client = clients_by_id.get(cid)
            if not client: continue

            print(f"\n{'─'*54}")
            print(f"  [{cid}] {client['name']}")
            print(f"{'─'*54}")

            # Bypass classification for demo consistency
            state = {
                "task_list": [{"route": "W1", "extracted_params": client}],
                "workflow_id": f"DEMO-{cid}",
                "logs": [],
                "workflow_results": []
            }
            final_state = orchestrator_graph.invoke(state)
            
            for l in final_state.get("logs", []): print(f"  {l}")

    finally:
        shutil.copyfile(backup, seed)
        if backup.exists(): backup.unlink()

    # ── W2 ────────────────────────────────────────────────
    print(log_section("W2 — Procurement to Payment"))

    with open(BASE / "data" / "purchase_orders.json", "r", encoding="utf-8") as f:
        pos = json.load(f)

    for po in pos[:3]: # Limit for demo brevity
        print(f"\n{'─'*54}")
        print(f"  [{po['po_no']}] vendor={po['vendor_id']} PO=₹{po['po_amount']:,}")
        print(f"{'─'*54}")

        state = {
            "task_list": [{"route": "W2", "extracted_params": po}],
            "workflow_id": f"DEMO-{po['po_no']}",
            "logs": [],
            "workflow_results": []
        }
        final_state = orchestrator_graph.invoke(state)
        for l in final_state.get("logs", []): print(f"  {l}")

    # ── W3 ────────────────────────────────────────────────
    print(log_section("W3 — Meeting to Task"))

    sample_notes = [
        (
            "WF-MTG-DEMO-1",
            "Team sync. Priya to update marketing deck for client by Friday. "
            "Neha will review the finance report and submit by month end. "
            "Vikram needs to set up the deployment pipeline before the next release. "
            "Sneha should prioritize finalizing the QA test plan by Wednesday.",
        )
    ]

    for wid, notes in sample_notes:
        print(f"\n{'─'*54}")
        print(f"  [{wid}]")
        print(f"{'─'*54}")

        state = {
            "task_list": [{"route": "W3", "extracted_params": {"notes": notes}}],
            "workflow_id": wid,
            "logs": [],
            "workflow_results": []
        }
        final_state = orchestrator_graph.invoke(state)
        for l in final_state.get("logs", []): print(f"  {l}")

    print(log_section("Demo Complete"))
    _print_db_summary()


# ─────────────────────────────────────────────────────────
# DB SUMMARY
# ─────────────────────────────────────────────────────────

def _print_db_summary():
    from shared.db import get_connection
    conn = get_connection()
    try:
        traces = conn.execute("SELECT COUNT(*) FROM traces").fetchone()[0]
        tasks  = conn.execute("SELECT COUNT(*) FROM tasks").fetchone()[0]
        alerts = conn.execute("SELECT COUNT(*) FROM systemic_alerts").fetchone()[0]
        pm     = conn.execute(
            "SELECT error_hash, attempts, success_rate, recommended_action "
            "FROM pattern_memory ORDER BY attempts DESC LIMIT 5"
        ).fetchall()
        
        print(f"\n  DB Summary:")
        print(f"    traces          : {traces} rows")
        print(f"    tasks           : {tasks} rows")
        print(f"    systemic_alerts : {alerts} rows")
        print(f"\n  Recent Pattern memory:")
        for r in pm:
            print(f"    {r['error_hash']:<26} "
                  f"attempts={r['attempts']:>3}  "
                  f"rate={r['success_rate']:.2f}  "
                  f"action={r['recommended_action']}")
    except Exception as e:
        print(f"  [DB Summary] Error: {e}")
    finally:
        conn.close()


# ─────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    if "--demo" in sys.argv:
        run_demo()
    else:
        run_interactive()
