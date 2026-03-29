import sqlite3
import json

conn = sqlite3.connect(r"c:\Users\karti\Downloads\bp\backend copy\data\auditpilot.db")
conn.row_factory = sqlite3.Row

wid = '53fc7099-68ce-4391-a91c-1c8b64f29c08'

# Check workflow status
workflow = conn.execute("SELECT * FROM workflows WHERE workflow_id = ?", (wid,)).fetchone()
print(f"WORKFLOW: {dict(workflow) if workflow else 'NOT FOUND'}")

# Check latest traces
traces = conn.execute("SELECT step_id, agent, status, error_type FROM traces WHERE workflow_id = ? ORDER BY created_at DESC LIMIT 5", (wid,)).fetchall()
for t in traces:
    print(f"TRACE: {dict(t)}")

conn.close()
