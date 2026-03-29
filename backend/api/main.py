from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path

# Ensure root is in path for relative imports in sub-packages
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

import os
os.environ["API_MODE"] = "1"

from api.routes import workflow, logs, traces, memory, explain, briefing, vendors
from modules.scheduler import start_scheduler, stop_scheduler

app = FastAPI(
    title="AuditPilot API",
    description="Backend API for the AuditAgent system",
    version="1.0.0"
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup/Shutdown Events
@app.on_event("startup")
def on_startup():
    start_scheduler()

@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()

# Include Routers
app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["Workflow"])
app.include_router(vendors.router, prefix="/api/v1/vendors", tags=["Vendors"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["Logs"])
app.include_router(traces.router, prefix="/api/v1/traces", tags=["Traces"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(explain.router, prefix="/api/v1", tags=["Explain"])
app.include_router(briefing.router, prefix="/api/v1/briefing", tags=["Briefing"])

@app.get("/")
async def root():
    return {"message": "AuditPilot API is running", "version": "1.0.0"}

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "message": "System Optimal"}
