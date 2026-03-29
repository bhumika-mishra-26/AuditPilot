AuditPilot
✈️ AuditPilot
Multi-Agent AI for Business Process Automation
Not another chatbot. A production-grade, autonomous AI orchestration system that executes complex enterprise workflows, learns from its own failures, and briefs you every morning before you open your laptop.


Python FastAPI LangGraph React SQLite OpenRouter


4 Workflows  ·  16+ AI Agents  ·  Real LLM Calls  ·  Cross-Workflow Memory  ·  Daily AI Briefings

📌 What is AuditPilot?
AuditPilot is a production-grade, multi-agent AI orchestration system that autonomously executes complex back-office business workflows — with memory, explainability, and proactive communication built in from day one.

Modern enterprises lose 40–60% of their operational bandwidth to three categories of repetitive work:

Problem	Status Quo	AuditPilot
🔁 Same error, no memory	Human retries manually every time	W4 pattern memory: success_rate ≥ 0.70 → auto-retry
🔕 Silent systemic failures	Nobody notices until 5 workflows fail	Systemic alert raised when same error hits 3+ workflows
📝 Meeting notes → lost tasks	Manual copy-paste into Jira/Notion	LLM extraction → owner resolution → task DB
🌑 No morning context	Check 3 dashboards every morning	LLM-written briefing delivered at 8:45 AM
🕳️ Opaque AI decisions	Black box, no audit trail	Every agent decision logged to SQLite traces
🏝️ Isolated workflows	No shared intelligence	All 3 workflows share one W4 pattern memory layer
🧠 System Architecture
┌─────────────────────────────────────────────────────────────────┐
│                    MASTER ORCHESTRATOR                          │
│         Intent Classification → State Builder → Dispatch       │
└──────────────┬───────────────┬──────────────────┬──────────────┘
               │               │                  │
       ┌───────▼──────┐ ┌──────▼──────┐  ┌───────▼──────┐
       │ W1 Onboarding│ │W2 Procurement│  │W3 Meeting    │
       │              │ │  to Payment  │  │Intelligence  │
       │ 6-node graph │ │ 7-node graph │  │ LLM + SQLite │
       └───────┬──────┘ └──────┬──────┘  └───────┬──────┘
               │   ERROR       │   ERROR          │   ERROR
               └───────────────▼──────────────────┘
                    ┌──────────────────────┐
                    │  W4 — PATTERN MEMORY │
                    │  T13 Detect          │
                    │  T14 Decide          │
                    │  T15 Alert           │
                    │  T16 Update          │
                    └──────────┬───────────┘
                               │
               ┌───────────────▼───────────────┐
               │   SQLite · APScheduler · SMTP  │
               │   Morning Briefing @ 8:45 AM   │
               └───────────────────────────────┘
🚀 Core Workflows
W1 — Client Onboarding Agent
Validates client data (GSTIN, email, duplicate check) and creates accounts with auto-retry on transient KYC failures.

Node	Function
validate_node	Schema validation: name, email (@), GSTIN (15 chars). Non-retryable on failure.
duplicate_node	Queries existing_clients.json. Raises DuplicateError → human review.
kyc_node	GSTIN verification. Simulates KYC_503 transient failure. Supports skip_kyc HITL override.
create_account_node	Writes record, logs client_id + timestamp.
error_node	Calls W4 run_w4(). Classifies retryable vs non-retryable. Manages retry_count.
audit_node	Logs workflow_id, final status, execution summary to traces. Always runs.
W2 — Procurement to Payment Agent
Three-way PO/invoice match, vendor authorization, approval routing, and payment execution with full audit trail.

Node	Function
intake_node	Logs PO number, initialises state fields.
validation_node	invoice_amount == po_amount. Raises THREE_WAY_MISMATCH if not.
vendor_check_node	Looks up vendor_id. Raises VENDOR_403 if inactive.
approval_node	Routes to approval if po_amount > ₹1,00,000. Auto-approves in demo.
payment_node	Simulates API_TIMEOUT on first attempt. Succeeds on retry.
orchestrator_node	Reads error type + pattern memory. API_TIMEOUT → retry · THREE_WAY_MISMATCH → manual · VENDOR_403 → escalate.
audit_node	Logs final status, retry count, execution metrics.
W3 — Meeting Intelligence Agent
Ingests raw unstructured meeting notes, calls LLM (Qwen 3.5-122B) to extract structured tasks, resolves owners, and dispatches assignments.

Node	Function
intake_node	Validates meeting notes have sufficient word count.
extraction_node	Real API call → qwen/qwen3.5-122b-a10b. Extracts {task, owner_name, deadline, priority, source_quote}. Up to 3 retries.
owner_resolution_node	Exact match → success · Ambiguous (two Rahuls) → escalated · Not found → escalated.
task_writer_node	Writes resolved tasks to tasks table in SQLite.
notification_node	Generates personalized assignment email per assignee. Logs to notification log.
W4 — Cross-Workflow Pattern Memory Engine
The architectural heart of AuditPilot. Never called by the Master Orchestrator — only invoked by W1, W2, and W3 error handlers. Shared intelligence across all workflows.

Every error from every workflow → shared pattern_memory table

T13: Detect Pattern     → cross-reference error_hash across workflow_ids
T14: Get Decision       → success_rate ≥ 0.70 → "retry" | < 0.70 → "escalate"
T15: Raise Alert        → fires when same error hits 3+ distinct workflows
T16: Update Pattern     → updates attempts, successes, success_rate after every resolution
This is not just error handling — it's organizational observability.
Unknown errors default to escalate (safe). Errors with 80% historical success are auto-retried. If a success rate drops below threshold, the system dynamically switches strategy.

✉️ Morning Briefing
APScheduler fires at 8:45 AM daily. The LLM synthesizes overnight traces into a human-readable briefing and delivers it via Gmail SMTP — before you open your laptop.

08:45 AM → APScheduler trigger
         → Query last 24h traces (grouped by workflow_type + status)
         → Read pattern_memory success rates
         → Pull unresolved systemic_alerts
         → LLM synthesis (300–500 word natural language briefing)
         → Gmail SMTP delivery
         → Log to briefing_log table
Also available on-demand: POST /briefing/generate

🏗️ Tech Stack
Backend
Technology	Role
Python 3.11+	Core language. Async-first with asyncio throughout.
LangGraph	StateGraph framework for all 4 agents + Master Orchestrator.
FastAPI + Uvicorn	REST API + SSE streaming. 10 endpoints.
aiosqlite	Async SQLite driver. All agent trace writes are non-blocking.
APScheduler	In-process scheduler. Morning briefing cron: 0 45 8 * * *
OpenRouter API	Auto-routing model selector for W3 + Master Orchestrator.
Gmail SMTP	TLS email delivery. App password authentication.
Pydantic v2	Request/response models.
Frontend
Technology	Role
React 18 + TypeScript + Vite	Core SPA framework
React Router v6	Protected routes, lazy loading
React Query (TanStack)	Server state, auto-caching, 5s polling for live runs
Zustand	Client state: active workflow_id, selected trace
Tailwind CSS + shadcn/ui	Utility-first styling
React Flow (@xyflow)	Agent graph visualization — nodes colored by status
Recharts	Dashboard metrics charts
Framer Motion	Page transitions, log stream animations
EventSource API	Native SSE for /explain streaming (Ask Why panel)
Data Layer
Table	Contents
workflows	workflow_id, workflow_type, status, created_at
traces	id, workflow_id, step, agent, status, message, timestamp
pattern_memory	error_hash, error_type, agent, recommended_action, attempts, successes, success_rate, last_seen_at, context, systemic_flag
systemic_alerts	id, error_hash, error_type, affected_workflows, context, created_at, resolved
tasks	id, workflow_id, task, owner_name, deadline, priority, source_quote, created_at
briefing_log	id, timestamp, subject, body, recipients, delivered
📡 API Reference
FastAPI backend on port 8000. Full OpenAPI docs at /docs.

Endpoint	Method	Description
/workflow/run	POST	Run a workflow. Returns {workflow_id, logs}.
/workflow/status	GET	Agent + status rows for a workflow_id.
/workflow/graph	GET	React Flow-compatible {nodes, edges} JSON.
/logs	GET	Timestamped trace rows. Filterable by status.
/traces	GET	All trace data. Filterable by outcome.
/memory	GET	Current pattern_memory.json contents.
/systemic-alerts	GET	Cross-workflow systemic alerts.
/workflow/resume	POST	HITL endpoint. Resume a paused workflow at a specific step.
/explain	POST	SSE — streams AI explanation of a workflow trace.
/briefing/generate	POST	Trigger on-demand morning briefing generation + email send.
⚡ Quick Start
Prerequisites
Python 3.11+
Node.js 18+
OpenRouter API key
Gmail App Password
1. Clone the repository
git clone https://github.com/janvee1201/AuditPilot.git
cd AuditPilot
2. Run the Backend
cd backend
pip install -r requirements.txt

# Initialize the database
python init_db.py

# Configure environment
cp .env.example .env
# Add OPENROUTER_API_KEY and GMAIL_APP_PASSWORD to .env

# Start the API server
python -m uvicorn api.main:app --reload --port 8000
3. Run the Frontend
cd frontend
npm install
npm run dev
4. Test a Workflow
# Run client onboarding
curl -X POST http://localhost:8000/workflow/run \
  -H "Content-Type: application/json" \
  -d '{
    "workflow_type": "onboarding",
    "input_payload": {
      "client_id": "C-001",
      "name": "Tech Corp",
      "email": "a@b.com",
      "gstin": "27AADCB2230M1Z2"
    }
  }'
Demo Sequence (Standalone)
cd backend
python main.py
# Runs: C-001 (success) → C-003 (duplicate) → C-005 (KYC retry via W4) → PO-1001 → meeting notes
📁 Project Structure
AuditPilot/
├── backend/
│   ├── api/                    # FastAPI endpoints (10 routes)
│   ├── orchestrator/           # Master Orchestrator — intent classification + dispatch
│   ├── w1/                     # Client Onboarding agent
│   │   ├── graph.py
│   │   ├── state.py
│   │   └── nodes/              # validation, duplicate, kyc, execution, error
│   ├── w2/                     # Procurement to Payment agent
│   │   ├── graph.py
│   │   ├── state.py
│   │   └── nodes/              # intake, validation, vendor_check, approval, payment, audit
│   ├── w3/                     # Meeting Intelligence agent
│   │   ├── pipeline.py
│   │   └── nodes/              # intake, extraction, owner_resolution, task_writer
│   ├── w4/                     # Cross-Workflow Pattern Memory engine
│   │   └── agent.py            # T13 / T14 / T15 / T16
│   ├── shared/                 # db.py · error_map.py · logger.py
│   ├── data/                   # clients.json · purchase_orders.json · vendors.json · team_members.json
│   ├── init_db.py              # One-time DB init + seed
│   ├── main.py                 # Master entry point
│   └── requirements.txt
│
└── frontend/
    ├── src/
    │   ├── components/         # React components
    │   ├── pages/              # Route pages
    │   └── ...
    ├── package.json
    └── vite.config.ts
💡 What Makes AuditPilot Novel
1. 🔗 Cross-Workflow Pattern Memory
No other system does this. W4 breaks workflow isolation. Errors in W1 inform decisions in W2. When the same error_hash appears across 3+ distinct workflows, it's declared systemic — enabling organization-wide observability, not just local debugging.

2. 🧮 Decision-Aware Retry Logic
Retry/escalate is not hard-coded. It's data-driven. Historical success_rate ≥ 0.70 → auto-retry. Unknown error → escalate (safe default). Success rate drops below threshold → system automatically switches strategy mid-operation.

3. 🤖 Real LLM in Production Data Path
W3 calls the actual Qwen 3.5-122B-A10B API. The LLM output (a JSON array of tasks) is parsed, validated, owner-resolved, and written to a database. This is a real agentic workflow — not a demo with mocked responses.

4. 🔄 Intent Classification with Clarification Loop
The Master Orchestrator classifies free-text input. If confidence < 0.85, it enters a clarification loop: asks a targeted question, appends the answer, and re-classifies. Mirrors how a real assistant handles ambiguity.

5. 📧 Morning Briefing as Product Intelligence
The briefing arrives in your inbox before you open your laptop. It's not a dashboard you have to visit — it's a fundamentally different product experience.

6. 🤝 Multi-Agent Collaboration
The Master Orchestrator can invoke multiple workflow agents in sequence or parallel for compound tasks. Agents share intermediate state through the centralized database and pattern memory.

🏆 Built For
GenAI Hackathon 2025
Powered by LangGraph · FastAPI · OpenRouter · SQLite · APScheduler

📄 License
MIT License — see LICENSE for details.

Four workflows. Sixteen agents. One shared intelligence.

AuditPilot — The future of intelligent business operations.

⭐ Star this repo if AuditPilot impressed you!
