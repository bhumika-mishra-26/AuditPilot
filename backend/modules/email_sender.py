"""
Module 6.3 — Email Sender
Sends the morning briefing via Gmail SMTP.
"""

import os
import sys
import smtplib
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import markdown
from pathlib import Path

load_dotenv()

# Ensure root is in sys.path
root = Path(__file__).resolve().parent.parent
if str(root) not in sys.path:
    sys.path.append(str(root))

from shared.db import get_connection

# ── Config — reads from .env ──────────────────────────────────
GMAIL_SENDER       = os.getenv("GMAIL_SENDER", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")
BRIEFING_RECIPIENT = os.getenv("BRIEFING_RECIPIENT", "")


def send_briefing_email(briefing_result: dict, recipient_email: str = None) -> dict:
    """
    Takes the dict returned by briefing_generator.generate_briefing()
    Sends it as a plain-text email via Gmail SMTP.

    Returns:
    { "status": "sent" | "failed", "to": "...", "reason": "..." }
    """

    # ── Validate config ───────────────────────────────────────
    if not GMAIL_SENDER or not GMAIL_APP_PASSWORD:
        return {
            "status": "failed",
            "reason": "GMAIL_SENDER or GMAIL_APP_PASSWORD not set in .env"
        }

    recipient = recipient_email or BRIEFING_RECIPIENT or GMAIL_SENDER  # send to self if not set

    # ── Build subject ─────────────────────────────────────────
    n = briefing_result.get("needs_action_count", 0)
    date_str = datetime.now().strftime("%d %b %Y")

    if n == 0:
        subject = f"AuditPilot morning briefing — {date_str} — all clear ✓"
    else:
        subject = f"AuditPilot morning briefing — {date_str} — {n} item{'s' if n > 1 else ''} need your attention"

    # ── Build HTML Body ───────────────────────────────────────
    action_color = "#e74c3c" if n > 0 else "#27ae60"
    generated_at = briefing_result.get("generated_at", "")
    workflow_count = briefing_result.get("workflow_count", 0)

    # Determine briefing type for header
    hour = datetime.now().hour
    if hour < 12:
        briefing_type = "Morning"
    elif hour < 17:
        briefing_type = "Afternoon"
    else:
        briefing_type = "Evening"

    # Convert briefing text (markdown-ish) to HTML
    briefing_html_content = markdown.markdown(briefing_result.get("briefing_text", "No briefing generated."))

    html_body = f"""
<!DOCTYPE html>
<html>
<head>
<style>
    body {{ font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; line-height: 1.6; color: #333; margin: 0; padding: 0; background-color: #f4f7f6; }}
    .container {{ max-width: 600px; margin: 20px auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.05); }}
    .header {{ background-color: #2c3e50; color: #ffffff; padding: 30px; text-align: center; }}
    .header h1 {{ margin: 0; font-size: 24px; letter-spacing: 1px; }}
    .header p {{ margin: 5px 0 0; opacity: 0.8; font-size: 14px; }}
    .stats-bar {{ display: table; width: 100%; background: #f8f9fa; border-bottom: 1px solid #eee; }}
    .stat-item {{ display: table-cell; padding: 15px; text-align: center; width: 50%; }}
    .stat-value {{ display: block; font-size: 20px; font-weight: bold; color: #2c3e50; }}
    .stat-label {{ display: block; font-size: 11px; text-transform: uppercase; color: #7f8c8d; }}
    .content {{ padding: 30px; }}
    .content h1, .content h2 {{ color: #2c3e50; border-bottom: 2px solid #18bc9c; padding-bottom: 5px; margin-top: 25px; font-size: 18px; }}
    .content ul {{ padding-left: 20px; }}
    .content li {{ margin-bottom: 10px; }}
    .footer {{ background: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; color: #95a5a6; border-top: 1px solid #eee; }}
    .footer a {{ color: #18bc9c; text-decoration: none; }}
</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>AuditPilot</h1>
            <p>{briefing_type} Briefing — {date_str}</p>
        </div>
        <div class="stats-bar">
            <div class="stat-item" style="border-right: 1px solid #eee;">
                <span class="stat-value">{workflow_count}</span>
                <span class="stat-label">Workflows Run</span>
            </div>
            <div class="stat-item">
                <span class="stat-value" style="color: {action_color};">{n}</span>
                <span class="stat-label">Actions Needed</span>
            </div>
        </div>
        <div class="content">
            {briefing_html_content}
        </div>
        <div class="footer">
            Generated: {generated_at} | <a href="http://localhost:8000">Open Dashboard</a>
            <br><br>
            — AuditPilot Assistant
        </div>
    </div>
</body>
</html>
"""

    # ── Build Plain Text Body ─────────────────────────────────
    plain_body = briefing_result.get("briefing_text", "No briefing generated.")
    plain_body += f"\n\n{'─' * 50}"
    plain_body += f"\nGenerated : {generated_at}"
    plain_body += f"\nWorkflows : {workflow_count}"
    plain_body += f"\n\n— AuditPilot  |  http://localhost:8000"

    # ── Build email ───────────────────────────────────────────
    msg = MIMEMultipart("alternative")
    msg["From"]    = GMAIL_SENDER
    msg["To"]      = recipient
    msg["Subject"] = subject
    msg.attach(MIMEText(plain_body, "plain"))
    msg.attach(MIMEText(html_body, "html"))

    # ── Send ──────────────────────────────────────────────────
    print(f"[email_sender] Connecting to Gmail SMTP...")
    try:
        with smtplib.SMTP("smtp.gmail.com", 587, timeout=15) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_SENDER, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_SENDER, [recipient], msg.as_string())

        print(f"[email_sender] ✓ Sent to {recipient}")
        print(f"[email_sender] Subject: {subject}")

        # ── Log to briefing_log table ─────────────────────────
        try:
            conn = get_connection()
            conn.execute("""
                INSERT INTO briefing_log
                    (briefing_date, items_count, email_sent, content)
                VALUES (?, ?, 1, ?)
            """, (
                datetime.now().strftime("%Y-%m-%d"),
                briefing_result.get("needs_action_count", 0),
                briefing_result.get("briefing_text", "")
            ))
            conn.commit()
            conn.close()
            print(f"[email_sender] Logged to briefing_log")
        except Exception as e:
            print(f"[email_sender] Warning: could not log to briefing_log — {e}")

        return {
            "status":  "sent",
            "to":      recipient,
            "subject": subject
        }

    except smtplib.SMTPAuthenticationError:
        reason = "Gmail auth failed. Check GMAIL_SENDER and GMAIL_APP_PASSWORD in .env"
        print(f"[email_sender] ✗ {reason}")
        return {"status": "failed", "reason": reason}

    except smtplib.SMTPException as e:
        reason = f"SMTP error: {str(e)}"
        print(f"[email_sender] ✗ {reason}")
        return {"status": "failed", "reason": reason}

    except Exception as e:
        reason = f"Unexpected error: {str(e)}"
        print(f"[email_sender] ✗ {reason}")
        return {"status": "failed", "reason": reason}