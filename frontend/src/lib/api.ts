const API_BASE = (import.meta as any).env?.VITE_API_URL || "http://localhost:8000";

// ── Health ────────────────────────────────────────────────

export async function checkBackendHealth(): Promise<boolean> {
  try {
    const res = await fetch(`${API_BASE}/api/v1/health`, { signal: AbortSignal.timeout(3000) });
    return res.ok;
  } catch {
    return false;
  }
}

// ── Workflow ─────────────────────────────────────────────

export interface WorkflowStartResponse {
  workflow_id: string;
  workflow_type: string;
  status: string;
}

export async function startWorkflow(prompt: string): Promise<WorkflowStartResponse> {
  const res = await fetch(`${API_BASE}/api/v1/workflow/start`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ prompt }),
  });
  if (!res.ok) throw new Error(`Start failed: ${res.statusText}`);
  return res.json();
}

export interface WorkflowStep {
  step_id: string;
  agent: string;
  status: string;
  created_at: string;
  error_type: string | null;
  decision_reason: string | null;
  log_message: string | null;
}

export interface WorkflowLog {
  timestamp: string;
  agent: string;
  message: string;
}

export interface WorkflowStatusResponse {
  workflow_id: string;
  state: string;
  type: string;
  steps: WorkflowStep[];
  patterns: any[];
  hitl_reason: string | null;
  hitl_options: string[];
  logs: WorkflowLog[];
  summary?: string | null;
}

export async function getWorkflowStatus(workflowId: string): Promise<WorkflowStatusResponse> {
  const res = await fetch(`${API_BASE}/api/v1/workflow/status/${workflowId}`);
  if (!res.ok) throw new Error(`Status failed: ${res.statusText}`);
  return res.json();
}

export async function resumeWorkflow(workflowId: string, input: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/workflow/resume/${workflowId}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input, human_resolution: input }),
  });
  if (!res.ok) throw new Error(`Resume failed: ${res.statusText}`);
  return res.json();
}

export interface WorkflowListItem {
  workflow_id: string;
  workflow_type: string;
  status: string;
  created_at: string;
}

export async function listWorkflows(limit = 20): Promise<WorkflowListItem[]> {
  const res = await fetch(`${API_BASE}/api/v1/workflow/list?limit=${limit}`);
  if (!res.ok) throw new Error(`List failed: ${res.statusText}`);
  return res.json();
}

// ── Logs ─────────────────────────────────────────────────

export interface LogEntry {
  timestamp: string;
  source: string;
  action: string;
  level: string;
  message: string;
}

export async function getLogs(workflowId?: string, limit = 50): Promise<LogEntry[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (workflowId) params.set("workflow_id", workflowId);
  const res = await fetch(`${API_BASE}/api/v1/logs?${params}`);
  if (!res.ok) throw new Error(`Logs failed: ${res.statusText}`);
  return res.json();
}

// ── Traces ───────────────────────────────────────────────

export async function getTraces(workflowId?: string, outcome?: string, limit = 100): Promise<any[]> {
  const params = new URLSearchParams({ limit: String(limit) });
  if (workflowId) params.set("workflow_id", workflowId);
  if (outcome) params.set("outcome", outcome);
  const res = await fetch(`${API_BASE}/api/v1/traces?${params}`);
  if (!res.ok) throw new Error(`Traces failed: ${res.statusText}`);
  return res.json();
}

// ── Memory ───────────────────────────────────────────────

export async function getPatternMemory(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/api/v1/memory`);
  if (!res.ok) throw new Error(`Memory failed: ${res.statusText}`);
  return res.json();
}

// ── Systemic Alerts ──────────────────────────────────────

export async function getSystemicAlerts(): Promise<any[]> {
  const res = await fetch(`${API_BASE}/api/v1/logs/systemic-alerts`);
  if (!res.ok) throw new Error(`Alerts failed: ${res.statusText}`);
  return res.json();
}

// ── Briefing ─────────────────────────────────────────────

export async function generateBriefing(email?: string): Promise<any> {
  const res = await fetch(`${API_BASE}/api/v1/briefing/generate`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(email ? { recipient_email: email } : {}),
  });
  if (!res.ok) throw new Error(`Briefing failed: ${res.statusText}`);
  return res.json();
}

export async function getBriefingHistory(limit = 10): Promise<any[]> {
  const res = await fetch(`${API_BASE}/api/v1/briefing/history?limit=${limit}`);
  if (!res.ok) throw new Error(`Briefing history failed: ${res.statusText}`);
  return res.json();
}

// ── Explain ──────────────────────────────────────────────

export async function explainWorkflow(workflowId: string, question: string): Promise<Response> {
  return fetch(`${API_BASE}/api/v1/explain`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ workflow_id: workflowId, question }),
  });
}

// ── Vendors ──────────────────────────────────────────────

export interface Vendor {
  vendor_id: string;
  name: string;
  status: string;
  risk: string;
  spend: string;
}

export async function listVendors(): Promise<Vendor[]> {
  const res = await fetch(`${API_BASE}/api/v1/vendors/`);
  if (!res.ok) throw new Error('Failed to fetch vendors');
  return res.json();
}

export async function onboardVendor(vendor: Omit<Vendor, 'status' | 'risk' | 'spend'>): Promise<Vendor> {
  const res = await fetch(`${API_BASE}/api/v1/vendors/`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...vendor,
      status: 'active',
      risk: 'Low',
      spend: '$0'
    }),
  });
  if (!res.ok) {
    const err = await res.json();
    throw new Error(err.detail || 'Failed to onboard vendor');
  }
  return res.json();
}
