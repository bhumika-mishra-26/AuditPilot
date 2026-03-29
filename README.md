# 🛡️ AuditPilot: Advanced Multi-Agent Audit System

AuditPilot is a high-fidelity, autonomous multi-agent system designed for streamlined client onboarding, vendor procurement, and meeting intelligence. It leverages **LangGraph**, **SQLModel**, and **FastAPI** to execute complex business workflows with human-in-the-loop (HITL) oversight.

---

## 🚀 Deployment Guide

### 1. Database Setup (Neon PostgreSQL)
1.  Create a free account at [Neon.tech](https://neon.tech).
2.  Create a new project and copy the **Connection String** (Postgres URL).
3.  Ensure the connection string ends with `?sslmode=require`.

### 2. Backend Deployment (Render)
1.  Connect your GitHub repository to [Render](https://render.com).
2.  Create a new **Web Service**.
3.  Choose the **Python** environment.
4.  Set the **Root Directory** to `backend`.
5.  **Build Command**: `pip install -r requirements.txt`
6.  **Start Command**: `gunicorn -k uvicorn.workers.UvicornWorker api.main:app --bind 0.0.0.0:$PORT`
7.  Add the following **Environment Variables**:
    - `DATABASE_URL`: Your Neon Postgres URL.
    - `OPENROUTER_API_KEY`: Your OpenRouter key.
    - `GMAIL_SENDER`: Your Gmail address.
    - `GMAIL_APP_PASSWORD`: Your 16-character Gmail App Password.
    - `BRIEFING_RECIPIENT`: Default email for system reports.
    - `API_MODE`: `1`

### 3. Frontend Deployment (Vercel)
1.  Connect your GitHub repository to [Vercel](https://vercel.com).
2.  Select the `frontend` directory as the project root.
3.  Vercel will auto-detect **Vite**.
4.  Add the following **Environment Variable**:
    - `VITE_API_URL`: The URL of your Render backend (e.g., `https://auditpilot-api.onrender.com`).
5.  Deploy!

---

## 🛠️ Local Development

### Backend
1.  `cd backend`
2.  `python -m venv venv`
3.  `source venv/bin/activate` (or `venv\Scripts\activate` on Windows)
4.  `pip install -r requirements.txt`
5.  `uvicorn api.main:app --reload`

### Frontend
1.  `cd frontend`
2.  `npm install`
3.  `npm run dev`

---

## 🏗️ Architecture
- **Engine**: LangGraph Multi-Agent Orchestrator.
- **Backend**: FastAPI, SQLModel (ORM), PostgreSQL.
- **Frontend**: React, Vite, Framer Motion, TailwindCSS.
- **Intelligence**: OpenRouter (Claude/GPT-4o).
