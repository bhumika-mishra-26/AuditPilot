# 🛡️ AuditPilot: Advanced Multi-Agent Audit System

AuditPilot is a high-fidelity, autonomous multi-agent orchestration system designed to streamline complex auditing operations—from structured client onboarding and deep vendor procurement checks, to extracting actionable intelligence from unstructured meetings. Built natively on top of a highly parallelized orchestration framework, AuditPilot executes intelligent workflows with seamless human-in-the-loop (HITL) oversight.

## 🚀 Key Features
- **Multi-Agent Orchestration**: Specialized algorithmic agents (Intake, Strategy, Execution, Validation) collaborate via LangGraph to reliably solve multi-stage audits.
- **Human-in-the-Loop (HITL)**: Intelligent breakpoints allow organizational administrators to review edge cases or override complex execution decisions before the system proceeds.
- **Pattern Memory**: The system intrinsically remembers recurring anomalies (e.g., specific cascading vendor failures or generic API timeouts) and dynamically improves its processing speed and error-mitigation logic.
- **Live Observability**: Real-time interactive UI powered by WebSockets to stream granular trace logs line-by-line as agents iteratively execute.

---

## 🏗️ Technology Stack

AuditPilot employs a modern, split-stack architecture engineered to ensure scalability, robust data permanence, and real-time execution tracking.

### **Frontend**
- **Framework**: React 18, Vite, TypeScript.
- **Styling**: TailwindCSS, Framer Motion (for high-fidelity fluid animations and transitions).
- **Icons & Assets**: Lucide React.
- **Deployment**: Vercel.

### **Backend**
- **Core Orchestrator**: LangGraph (for stateful multi-agent node management), LangChain.
- **API Engine**: FastAPI running on Uvicorn & Gunicorn.
- **Database & ORM**: Neon PostgreSQL accessed asynchronously via SQLModel.
- **Intelligence Model**: OpenRouter (Claude 3.5 Sonnet / GPT-4o).
- **Deployment**: Render.

---

## ⚙️ The Multi-Agent Workflow Engine

At the heart of AuditPilot is the **LangGraph Orchestrator**, executing across multiple predefined workflow architectures (`W1`: Onboarding, `W2`: Auditing, `W3`: Meeting Intelligence, `W4`: Task Extraction). An overarching node-graph coordinates the highly-typed "state" of an operation as it flows from one autonomous node to the next.

1. **Intake Agent**: Standardizes and validates the incoming raw prompt or context file.
2. **Strategy Agent**: Formulates a highly structured execution path specific to the detected workflow type.
3. **Execution Agent**: Performs the heavy computational lifting—validating external GSTIN inputs, assigning operational roles, or parsing unstructured input.
4. **Validation Agent**: Cross-references outputs against strict organizational rules. If confidence drops below a threshold, the workflow gracefully falls into a **Human-In-The-Loop (HITL)** fallback state.

---

## 🔄 The Data Lifecycle

### 1. Data Inserting (Ingestion)
Data enters the AuditPilot ecosystem sequentially from multiple entry points:
- **Client Endpoints**: An authenticated user triggers an operation via the Frontend's `Ask AI` prompt modal, hitting the `POST /api/v1/workflow/start` REST endpoint on the backend.
- **Internal Database Seeding**: Pre-configured `init_db.py` initialization scripts natively insert required initial state data (like Vendor specifications, past Systemic patterns, and organization structure) seamlessly into the remote Neon PostgreSQL database via SQLModel.

### 2. Data Collecting (Fetching & Context)
Before generating insights, the orchestrator enriches user prompts with historical and systemic context:
- **Intake Parsing**: Raw prompts and input parameters are extracted, cleaned, and normalized.
- **Pattern Memory Extraction**: The system queries the `PatternMemory` database table behind the scenes to check if a statistically similar error has been encountered historically, applying learned mitigation strategies before execution begins.

### 3. Data Processing (Agentic Execution)
The enriched dataset strictly flows through the LangGraph node architecture:
- **Intake -> Execution -> Validation**: Depending on the specific workflow schema, algorithmic agents recursively execute their logic loops, passing a shared `State` object down the sequence.
- **Trace Logging**: Throughout the entire execution path, individual nodes emit raw string logs. The backend formats these logs and writes them securely to the `traces` and `logs` database tables globally mapped in Indian Standard Time (IST).
- **Human-In-The-Loop**: If the Validation Agent flags a categorical discrepancy (e.g., a Vendor risk score is unusually high), the workflow execution pauses globally and assigns a manual human-resolution toggle directly to the Frontend dashboard.

### 4. Final Results (Output)
Once a workflow successfully traverses the final `<END>` node, the system wraps up operations:
- **Database Commit**: The final structured state (e.g., extracted action items, validated vendor credentials, or onboarding emails) is finalized within the Neon Database.
- **Real-time Notifications**: Real-time component status indicators in the React dashboard dynamically shift to **"Completed"**, and the user is provided an interactive markdown summary.
- **Automation Pipeline**: Embedded `smtplib` polling scripts asynchronously parse the final operation outcomes and autonomously fire off daily email briefings or system-wide anomaly alerts to assigned administrators.

---

## 💻 Deployment Guide

### 1. Database Setup (Neon PostgreSQL)
1. Create a free account at [Neon.tech](https://neon.tech).
2. Create a new project and copy the **Connection String** (Postgres URL).
3. Ensure the connection string ends with `?sslmode=require`.

### 2. Backend Deployment (Render)
1. Connect your GitHub repository to [Render](https://render.com).
2. Create a new **Web Service**.
3. Choose the **Python** environment.
4. Set the **Root Directory** to `backend`.
5. **Build Command**: `pip install -r requirements.txt`
6. **Start Command**: `gunicorn -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:$PORT`
7. Add the following **Environment Variables**:
   - `DATABASE_URL`: Your Neon Postgres URL.
   - `OPENROUTER_API_KEY`: Your OpenRouter key.
   - `GMAIL_SENDER`: Admin Gmail address.
   - `GMAIL_APP_PASSWORD`: Your 16-character Gmail App Password.
   - `BRIEFING_RECIPIENT`: Default email for system reports.
   - `API_MODE`: `1`

### 3. Frontend Deployment (Vercel)
1. Connect your GitHub repository to [Vercel](https://vercel.com).
2. Select the `frontend` directory as the project root.
3. Vercel will auto-detect **Vite**.
4. Add the following **Environment Variable**:
   - `VITE_API_URL`: The URL of your Render backend (e.g., `https://auditpilot-api.onrender.com`).
5. Deploy!

---

## 🛠️ Local Development

### Backend
1. `cd backend`
2. `python -m venv venv`
3. `source venv/bin/activate` *(Windows: `venv\Scripts\activate`)*
4. `pip install -r requirements.txt`
5. `uvicorn api.main:app --reload`

### Frontend
1. `cd frontend`
2. `npm install`
3. `npm run dev`

---

*Built with precision for the modern era of autonomous intelligence.*
