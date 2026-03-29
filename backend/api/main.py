from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import sys
from pathlib import Path
import os

# Ensure root is in path
BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

os.environ["API_MODE"] = "1"

<<<<<<< HEAD
from dotenv import load_dotenv
load_dotenv()

from api.routes import workflow, logs, traces, memory, explain, briefing, vendors
from modules.scheduler import start_scheduler, stop_scheduler

=======
# Create app FIRST
>>>>>>> upstream/main
app = FastAPI(
    title="AuditPilot API",
    description="Backend API for the AuditAgent system",
    version="1.0.0"
)

# ✅ CORS MIDDLEWARE (MUST BE RIGHT AFTER APP INIT)
origins = [
    "https://audit-pilot-lemon.vercel.app",
    "http://localhost:3000",  # local dev
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],  # helps with auth/debugging
)

# NOW import routes (after middleware setup)
from api.routes import workflow, logs, traces, memory, explain, briefing, vendors
from modules.scheduler import start_scheduler, stop_scheduler

# Startup/Shutdown Events
@app.on_event("startup")
def on_startup():
    start_scheduler()

@app.on_event("shutdown")
def on_shutdown():
    stop_scheduler()

# Routes
app.include_router(workflow.router, prefix="/api/v1/workflow", tags=["Workflow"])
app.include_router(vendors.router, prefix="/api/v1/vendors", tags=["Vendors"])
app.include_router(logs.router, prefix="/api/v1/logs", tags=["Logs"])
app.include_router(traces.router, prefix="/api/v1/traces", tags=["Traces"])
app.include_router(memory.router, prefix="/api/v1/memory", tags=["Memory"])
app.include_router(explain.router, prefix="/api/v1", tags=["Explain"])
app.include_router(briefing.router, prefix="/api/v1/briefing", tags=["Briefing"])

# Root
@app.get("/")
async def root():
    return {"message": "AuditPilot API is running", "version": "1.0.0"}

# Health
@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "message": "System Optimal"}
