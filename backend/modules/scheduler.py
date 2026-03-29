"""
Module 6.4 — Scheduler
Runs the full briefing pipeline (generate + email) on a daily cron.
"""

import sys
import os
from pathlib import Path
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import time

# Ensure root is in sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.append(str(root))

from modules.briefing_generator import generate_briefing, get_traces_from_db
from modules.email_sender import send_briefing_email

# ── Single shared scheduler instance ─────────────────────────
_scheduler = BackgroundScheduler()


def run_briefing_job(traces: list = None, recipient_email: str = None) -> dict:
    """
    Generates briefing and sends email.
    """
    print(f"\n[scheduler] Briefing job started — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    if traces is None:
        traces = get_traces_from_db(hours=8)
        print(f"[scheduler] Pulled {len(traces)} traces from DB")

    briefing = generate_briefing(traces)
    print(f"[scheduler] Briefing generated — {briefing['workflow_count']} workflows, "
          f"{briefing['needs_action_count']} need action")

    email_result = send_briefing_email(briefing, recipient_email)
    print(f"[scheduler] Email — status={email_result['status']}")

    return {
        "briefing_text":      briefing["briefing_text"],
        "workflow_count":     briefing["workflow_count"],
        "needs_action_count": briefing["needs_action_count"],
        "generated_at":       briefing["generated_at"],
        "email_status":       email_result["status"],
        "email_to":           email_result.get("to", ""),
        "email_reason":       email_result.get("reason", "")
    }


def start_scheduler():
    if _scheduler.running:
        print("[scheduler] Already running")
        return

    _scheduler.add_job(
        run_briefing_job,
        trigger=CronTrigger(hour=8, minute=45),
        id="morning_briefing",
        name="AuditPilot morning briefing",
        replace_existing=True
    )

    _scheduler.start()
    print("[scheduler] ✓ Started — briefing runs daily at 08:45")


def stop_scheduler():
    if _scheduler.running:
        _scheduler.shutdown(wait=False)
        print("[scheduler] Stopped")