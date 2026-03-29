import sqlite3, json

conn = sqlite3.connect("auditpilot.db")
conn.row_factory = sqlite3.Row

# Recent workflows
print("=== RECENT WORKFLOWS ===")
wfs = conn.execute("SELECT workflow_id, workflow_type, status, created_at FROM workflows ORDER BY created_at DESC LIMIT 5").fetchall()
for w in wfs:
    print(f"  {w['workflow_id'][:30]}  type={w['workflow_type']:15s}  status={w['status']:12s}  at={w['created_at']}")

# Check traces for the latest escalated meeting workflow
print("\n=== TRACES FOR LATEST MEETING WORKFLOW ===")
latest = conn.execute("SELECT workflow_id FROM workflows WHERE workflow_type='meeting' ORDER BY created_at DESC LIMIT 1").fetchone()
if latest:
    wid = latest['workflow_id']
    print(f"  workflow_id: {wid}")
    traces = conn.execute("SELECT step_id, agent, status, error_type, log_message, decision_reason FROM traces WHERE workflow_id = ? ORDER BY created_at ASC", (wid,)).fetchall()
    if not traces:
        # Try with WF- prefix variations
        traces = conn.execute("SELECT step_id, agent, status, error_type, log_message FROM traces WHERE workflow_id LIKE ? ORDER BY created_at ASC", (f"%{wid[:8]}%",)).fetchall()
    for t in traces:
        print(f"  {t['step_id']:30s}  status={t['status']:12s}  error={t['error_type']}  msg={t['log_message']}")
    if not traces:
        print("  (no traces found)")
else:
    print("  No meeting workflow found")

# Check all recent traces
print("\n=== ALL RECENT TRACES ===")
all_traces = conn.execute("SELECT workflow_id, step_id, status, error_type FROM traces ORDER BY created_at DESC LIMIT 15").fetchall()
for t in all_traces:
    print(f"  {t['workflow_id'][:25]:25s}  {t['step_id']:30s}  status={t['status']:12s}  error={t['error_type']}")

# Check input_payload for the latest meeting workflow
print("\n=== INPUT PAYLOAD ===")
if latest:
    wp = conn.execute("SELECT input_payload FROM workflows WHERE workflow_id = ?", (latest['workflow_id'],)).fetchone()
    if wp and wp['input_payload']:
        print(f"  {wp['input_payload'][:300]}")

conn.close()
