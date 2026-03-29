import React, { useState, useEffect, useRef, useCallback } from 'react';
import { createPortal } from 'react-dom';
import { Play, CheckCircle2, XCircle, AlertCircle, Clock, Search, ChevronRight, Terminal as TerminalIcon, User, FileText, Settings, CreditCard, Store, Plus, X, Loader2, Command, Send, AlertTriangle, CheckCircle, Sparkles, Lock } from 'lucide-react';
import { motion, AnimatePresence } from 'motion/react';
import CyberCard from '../ui/CyberCard';
import { MagicGrid, MagicCard } from '../ui/MagicBento';
import WavyCard from '../ui/WavyCard';
import AgentPlan from '../ui/agent-plan';
import {
  startWorkflow,
  getWorkflowStatus,
  resumeWorkflow,
  getTraces,
  onboardVendor,
  generateBriefing,
  type WorkflowStatusResponse,
} from '../../lib/api';
import BlurText from '../ui/BlurText';
import { staggerContainer, itemVariants } from '../ui/PageTransition';
import MarkdownRenderer from '../ui/MarkdownRenderer';
import AskAI from '../ui/AskAI';

interface LiveLog {
  timestamp: string;
  agent: string;
  status: string;
  message: string;
}

export default function DashboardScreen() {
  const [query, setQuery] = useState('');
  const [isExecuting, setIsExecuting] = useState(false);
  const [activeTaskId, setActiveTaskId] = useState<string | undefined>();
  const [logs, setLogs] = useState<LiveLog[]>([]);
  const [workflowId, setWorkflowId] = useState<string | null>(null);
  const [workflowState, setWorkflowState] = useState<string>('idle');
  const [hitlReason, setHitlReason] = useState<string | null>(null);
  const [hitlOptions, setHitlOptions] = useState<string[]>([]);
  const [hitlInput, setHitlInput] = useState('');
  const [isResuming, setIsResuming] = useState(false);
  
  // Vendor Onboarding State
  const [showVendorModal, setShowVendorModal] = useState(false);
  const [newVendor, setNewVendor] = useState({ vendor_id: '', name: '' });
  const [isSubmittingVendor, setIsSubmittingVendor] = useState(false);
  const [vendorError, setVendorError] = useState<string | null>(null);
  
  const [error, setError] = useState<string | null>(null);

  // KPI state
  const [totalTraces, setTotalTraces] = useState(0);
  const [escalationCount, setEscalationCount] = useState(0);

  // Briefing state
  const [briefingText, setBriefingText] = useState<string | null>(null);
  const [generatingBriefing, setGeneratingBriefing] = useState(false);
  const [showBriefingModal, setShowBriefingModal] = useState(false);
  const [briefingEmail, setBriefingEmail] = useState('');
  
  // Result Modal State
  const [showResultModal, setShowResultModal] = useState(false);
  const [workflowSummary, setWorkflowSummary] = useState<string | null>(`What happened in this workflow?
**High‑level picture**

The workflow \`e3bbd1c8‑c580‑4ee3‑a759‑927c5d4f74f9\` is a typical “receive‑an‑inquiry → figure‑out‑who‑owns‑it → create‑a‑task → hand it off to a downstream sub‑workflow (W3)” process.  

---

### 1. Starting the workflow
| Trace line | What happened |
|------------|--------------|
| \`master_orchestrator – intent_classification\` | **Success**: Intent identified as ticket creation. |
| \`master_orchestrator – state_building\` | **Success**: Context object initialized. |

### 2. Escalation Overview
The system hit an **ambiguous owner** situation. Because its confidence score was too low, it escalated the decision to a human via the \`w4_agent\`.

Overall, the workflow *completed* but had to pause and be escalated once because the automated owner‑lookup could not pick a single owner.`);

  const logsEndRef = useRef<HTMLDivElement>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    const el = logsEndRef.current;
    if (el) el.parentElement?.scrollTo({ top: el.parentElement.scrollHeight, behavior: "smooth" });
  }, [logs]);

  // Fetch KPI data on mount
  useEffect(() => {
    getTraces().then(traces => {
      setTotalTraces(traces.length);
      setEscalationCount(traces.filter(t => t.status === 'escalated').length);
    }).catch(() => {});
  }, [workflowState]);

  const handleGenerateBriefing = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    setShowBriefingModal(false);
    setGeneratingBriefing(true);
    setBriefingText(null);
    try {
      const result = await generateBriefing(briefingEmail || undefined);
      setBriefingText(result.briefing_text || "Automated Briefing Complete. No new anomalies.");
      setBriefingEmail(''); // reset after use
    } catch (e: any) {
      console.error(e);
      setBriefingText("Failed to generate briefing. " + e.message);
    } finally {
      setGeneratingBriefing(false);
    }
  };

  // Polling logic
  const startPolling = useCallback((wfId: string) => {
    if (pollRef.current) clearInterval(pollRef.current);
    
    const poll = async () => {
      try {
        const status: WorkflowStatusResponse = await getWorkflowStatus(wfId);
        
        const liveLogs: LiveLog[] = status.logs.map(l => ({
          timestamp: l.timestamp ? new Date(l.timestamp).toLocaleTimeString('en-US', { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' }) : '',
          agent: l.agent || 'System',
          status: 'OK',
          message: l.message || '',
        }));
        setLogs(liveLogs);
        setWorkflowState(status.state);

        const typeMap: Record<string, string> = { onboarding: 'W1', procurement: 'W2', meeting: 'W3' };
        setActiveTaskId(typeMap[status.type] || 'W1');

        if (status.state === 'escalated') {
          setHitlReason(status.hitl_reason);
          setHitlOptions(status.hitl_options || []);
          setIsExecuting(false);
        } else if (status.state === 'completed' || status.state === 'failed') {
          setIsExecuting(false);
          setWorkflowSummary(status.summary || null);
          if (status.state === 'completed') {
            setShowResultModal(true);
          }
          if (pollRef.current) clearInterval(pollRef.current);
        }
      } catch (err: any) {
        console.error('Poll error:', err.message);
      }
    };

    poll();
    pollRef.current = setInterval(poll, 2000);
  }, []);

  useEffect(() => {
    return () => { if (pollRef.current) clearInterval(pollRef.current); };
  }, []);

  const handleExecute = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || isExecuting) return;

    // Gating Logic
    const activePlan = localStorage.getItem('auditpilot_plan') || 'free';
    const lowerQuery = query.toLowerCase();
    if (activePlan === 'free') {
      if (lowerQuery.includes('meeting') || lowerQuery.includes('procurement') || lowerQuery.includes('invoice') || lowerQuery.includes('contract')) {
        setError("🔒 Please upgrade to the Pro Tier to unlock W2 (Procurement) & W3 (Meeting) workflows.");
        return;
      }
    }

    setError(null);
    setLogs([]);
    setHitlReason(null);
    setHitlOptions([]);
    setWorkflowState('running');
    setWorkflowSummary(null);
    setShowResultModal(false);
    setIsExecuting(true);

    try {
      const result = await startWorkflow(query);
      setWorkflowId(result.workflow_id);
      const typeMap: Record<string, string> = { onboarding: 'W1', procurement: 'W2', meeting: 'W3' };
      setActiveTaskId(typeMap[result.workflow_type] || 'W1');
      startPolling(result.workflow_id);
    } catch (err: any) {
      setError(err.message || 'Failed to start workflow.');
      setIsExecuting(false);
      setWorkflowState('failed');
    }
  };

  const handleResume = async (optionOrInput: string) => {
    if (!workflowId) return;
    setIsResuming(true);
    setError(null);

    try {
      await resumeWorkflow(workflowId, optionOrInput);
      setHitlReason(null);
      setHitlOptions([]);
      setHitlInput('');
      setIsExecuting(true);
      setWorkflowState('running');
      startPolling(workflowId);
    } catch (err: any) {
      setError(err.message || 'Failed to resume workflow.');
    } finally {
      setIsResuming(false);
    }
  };

  const handleOnboardVendor = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newVendor.vendor_id || !newVendor.name) return;
    setIsSubmittingVendor(true);
    setVendorError(null);
    try {
      await onboardVendor(newVendor);
      setShowVendorModal(false);
      setNewVendor({ vendor_id: '', name: '' });
      // After onboarding, we auto-resume the workflow
      handleResume('1 (continue)');
    } catch (err: any) {
      setVendorError(err.message || 'Onboarding failed');
    } finally {
      setIsSubmittingVendor(false);
    }
  };

  const handleHitlSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (hitlInput.trim()) {
      handleResume(hitlInput.trim());
    }
  };

  const statusColor = workflowState === 'completed' ? 'text-emerald-400' : workflowState === 'failed' ? 'text-red-400' : workflowState === 'escalated' ? 'text-indigo-400' : workflowState === 'running' ? 'text-indigo-400' : 'text-gray-500';
  const statusDot = workflowState === 'completed' ? 'bg-emerald-400' : workflowState === 'failed' ? 'bg-red-400' : workflowState === 'escalated' ? 'bg-indigo-400 animate-pulse' : workflowState === 'running' ? 'bg-indigo-400 animate-pulse' : 'bg-gray-500';

  return (
    <motion.div
      initial="initial"
      animate="animate"
      variants={staggerContainer}
      className="space-y-10 pb-20 relative"
    >
      {/* Cinematic Processing Glow Overlay */}
      <AnimatePresence>
        {isExecuting && (
          <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="processing-bg fixed inset-0 z-0"
          />
        )}
      </AnimatePresence>
      {/* Query Input Section and Briefing */}
      <motion.div variants={itemVariants} className="grid grid-cols-1 xl:grid-cols-3 gap-8 relative z-10">
        <div className="xl:col-span-2">
          <WavyCard
            color="rgb(99, 102, 241)"
            filterId="turbulent-displace-dashboard"
            containerClassName="w-full h-full"
            className="bg-black/80 backdrop-blur-xl p-8 border border-indigo-500/20 shadow-[0_0_50px_rgba(99,102,241,0.1)] h-full"
          >
            <div className="flex flex-col md:flex-row gap-6 items-center w-full pb-8">
              <div className="flex-shrink-0 w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center shadow-[0_0_30px_rgba(99,102,241,0.2)]">
                <Command className="w-8 h-8 text-indigo-400" />
              </div>
              <div className="flex-1 w-full">
                <h2 className="text-xl font-bold text-white mb-2 font-heading tracking-tight text-left">Intelligence Engine Interface</h2>
                <p className="text-sm text-gray-400 font-mono mb-4 uppercase tracking-widest text-left">Execute natural language workflow queries against the backend</p>

                <form onSubmit={handleExecute} className="relative group">
                  <div className="absolute -inset-1 bg-gradient-to-r from-indigo-500 via-purple-500 to-indigo-500 rounded-xl blur opacity-25 group-hover:opacity-50 transition duration-1000 group-hover:duration-200 animate-gradient-x"></div>
                  <div className="relative flex items-center bg-black border border-white/10 rounded-xl overflow-hidden focus-within:border-indigo-500/50 transition-colors">
                    <input
                      type="text"
                      value={query}
                      onChange={(e) => setQuery(e.target.value)}
                      placeholder="e.g., Onboard Acme Corp with email acme@corp.com..."
                      className="w-full bg-transparent border-none px-6 py-4 text-white placeholder:text-gray-600 focus:outline-none focus:ring-0 font-mono text-sm"
                      disabled={isExecuting}
                    />
                    <button
                      type="submit"
                      disabled={!query.trim() || isExecuting}
                      className="bg-indigo-600 hover:bg-indigo-500 disabled:bg-white/5 disabled:text-gray-500 text-white px-8 py-4 font-bold tracking-widest uppercase text-xs transition-colors flex items-center gap-2 border-l border-white/10"
                    >
                      {isExecuting ? 'Running...' : 'Run'}
                      {!isExecuting && <Play className="w-3 h-3 fill-current" />}
                    </button>
                  </div>
                </form>

                {error && (
                  <div className="mt-3 flex items-center gap-2 text-red-400 text-xs font-mono bg-red-500/10 border border-red-500/20 rounded-lg px-4 py-2">
                    <XCircle className="w-4 h-4 flex-shrink-0" />
                    {error}
                  </div>
                )}
              </div>
            </div>
          </WavyCard>
        </div>

        {/* Pulse Briefing Container */}
        <div className="xl:col-span-1 border border-white/10 rounded-2xl bg-black/40 overflow-hidden flex flex-col shadow-[0_0_40px_rgba(0,0,0,0.5)] h-full">
          <div className="px-6 py-4 border-b border-white/5 bg-indigo-500/5 flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-indigo-400" />
              <h2 className="text-xs font-bold font-mono tracking-widest text-indigo-300 uppercase">System Pulse</h2>
            </div>
            <button 
              onClick={() => {
                setShowBriefingModal(true);
              }}
              disabled={generatingBriefing}
              className={`px-3 py-1.5 font-bold rounded-lg text-[10px] uppercase tracking-wider flex items-center gap-1 transition-colors bg-indigo-500 text-white hover:bg-indigo-400 disabled:opacity-50`}
            >
              {generatingBriefing ? <Loader2 className="w-3 h-3 animate-spin" /> : <Sparkles className="w-3 h-3" />}
              Run Briefing
            </button>
          </div>
          <div className="p-6 flex-1 text-sm text-gray-300 flex items-center justify-center overflow-y-auto">
            {generatingBriefing ? (
              <div className="flex flex-col items-center gap-4 text-indigo-400 opacity-50">
                <div className="flex items-center gap-2">
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-ping"></div>
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-ping delay-75"></div>
                  <div className="w-2 h-2 rounded-full bg-indigo-400 animate-ping delay-150"></div>
                </div>
                <p className="font-mono text-[10px] uppercase tracking-widest text-center">Synthesizing<br />Telemetry Data</p>
              </div>
            ) : briefingText ? (
              <div className="prose prose-invert prose-p:leading-relaxed prose-sm max-w-none text-left w-full h-full custom-scrollbar overflow-y-auto">
                <MarkdownRenderer content={briefingText} />
              </div>
            ) : (
              <div className="text-center opacity-30">
                <FileText className="w-8 h-8 mx-auto mb-2" />
                <p className="font-mono text-[10px] uppercase tracking-widest">No Active Briefing</p>
              </div>
            )}
          </div>
        </div>
      </motion.div>

      {/* HITL Intervention Panel */}
      <AnimatePresence>
        {hitlReason && workflowState === 'escalated' && (
          <motion.div
            initial={{ opacity: 0, y: 20, scale: 0.98 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: -10, scale: 0.98 }}
            className="border border-indigo-500/30 bg-indigo-500/5 rounded-2xl p-6 backdrop-blur-xl shadow-[0_0_40px_rgba(99,102,241,0.1)]"
          >
            <div className="flex items-start gap-4 text-left">
              <div className="w-10 h-10 rounded-xl bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center flex-shrink-0">
                <AlertCircle className="w-5 h-5 text-indigo-400" />
              </div>
              <div className="flex-1">
                <h3 className="text-indigo-400 font-bold text-sm uppercase tracking-wider mb-1">Human Input Required</h3>
                <p className="text-gray-300 text-sm mb-4">{hitlReason}</p>

                {hitlOptions.length > 0 && (
                  <div className="flex flex-wrap gap-2 mb-4">
                    {hitlOptions.map((opt) => (
                      <button
                        key={opt}
                        onClick={() => {
                          if (opt === 'onboard_vendor') {
                            const match = hitlReason?.match(/V-\d+/);
                            if (match) setNewVendor(prev => ({ ...prev, vendor_id: match[0] }));
                            setShowVendorModal(true);
                          } else {
                            handleResume(opt);
                          }
                        }}
                        disabled={isResuming}
                        className="px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 rounded-lg text-sm font-medium text-white transition-all capitalize disabled:opacity-50"
                      >
                        {opt.replace(/_/g, ' ')}
                      </button>
                    ))}
                  </div>
                )}

                <form onSubmit={handleHitlSubmit} className="flex gap-2">
                  <input
                    type="text"
                    value={hitlInput}
                    onChange={(e) => setHitlInput(e.target.value)}
                    placeholder="Type your response here..."
                    className="flex-1 bg-black/50 border border-white/10 rounded-lg px-4 py-2 text-sm text-white placeholder:text-gray-600 focus:outline-none focus:border-indigo-500/50"
                    disabled={isResuming}
                  />
                  <button
                    type="submit"
                    disabled={!hitlInput.trim() || isResuming}
                    className="px-4 py-2 bg-indigo-500 hover:bg-indigo-400 text-white font-bold rounded-lg text-xs uppercase tracking-wider transition-colors disabled:opacity-50 flex items-center gap-1"
                  >
                    {isResuming ? <Loader2 className="w-3 h-3 animate-spin" /> : <Send className="w-3 h-3" />}
                    Submit
                  </button>
                </form>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Dynamic Execution View */}
      <motion.div 
        variants={itemVariants}
        className={`transition-all duration-1000 relative z-10 ${isExecuting || logs.length > 0 ? 'opacity-100 translate-y-0' : 'opacity-50 translate-y-4 filter grayscale-[50%]'}`}
      >
        <MagicGrid className="lg:grid-cols-2 gap-8">
          <MagicCard className="col-span-1 p-0 flex flex-col h-[600px] overflow-hidden bg-black/40 border border-white/10 text-left" gradientColor="#ec4899">
            <div className="px-8 pt-8 pb-4 flex items-center justify-between border-b border-white/5 bg-black/60 relative z-20">
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-black font-heading tracking-tight text-white uppercase text-left">Multi-Agent Workflow</h2>
                <div className={`flex items-center gap-2 px-3 py-1 rounded-full border ${isExecuting ? 'bg-emerald-500/10 border-emerald-500/30' : workflowState === 'escalated' ? 'bg-indigo-500/10 border-indigo-500/30' : workflowState === 'completed' ? 'bg-emerald-500/10 border-emerald-500/30' : 'bg-white/5 border-white/10'}`}>
                  <span className={`w-2 h-2 rounded-full ${statusDot}`}></span>
                  <span className={`text-[10px] font-bold uppercase tracking-widest ${statusColor}`}>
                    {workflowState === 'idle' ? 'Standby' : workflowState}
                  </span>
                </div>
              </div>
            </div>
            <div className="flex-1 relative bg-black/20 p-4 overflow-y-auto">
              <AgentPlan 
                activeTaskId={(isExecuting || workflowState !== 'idle') ? activeTaskId : undefined} 
                overallStatus={workflowState}
              />
            </div>
          </MagicCard>

          <MagicCard className="col-span-1 p-0 flex flex-col h-[600px] bg-black/60 border border-white/10 text-left" gradientColor="#6366f1">
            <div className="px-8 pt-8 pb-4 flex items-center justify-between border-b border-white/5 relative z-20">
              <div className="flex items-center gap-3">
                <h2 className="text-xl font-black font-heading tracking-tight text-white uppercase text-left">Live Console</h2>
                <TerminalIcon className="w-5 h-5 text-indigo-400 opacity-50" />
              </div>
            </div>

            <div className="flex-1 p-6 font-mono text-xs overflow-y-auto relative text-left">
              <div className="absolute inset-0 pointer-events-none bg-[linear-gradient(rgba(255,255,255,0)_50%,rgba(0,0,0,0.25)_50%),linear-gradient(90deg,rgba(255,0,0,0.06),rgba(0,255,0,0.02),rgba(0,0,255,0.06))] bg-[length:100%_4px,3px_100%] opacity-20" />
              <div className="space-y-4 relative z-10">
                {logs.length === 0 && !isExecuting && (
                  <div className="text-gray-600 flex flex-col items-center justify-center h-full gap-4 opacity-50">
                    <TerminalIcon className="w-12 h-12" />
                    <p>Awaiting query execution...</p>
                  </div>
                )}
                {logs.map((log, i) => (
                  <div key={`${workflowId}-${i}`} className="flex gap-4">
                    <span className="text-gray-500 shrink-0">[{log.timestamp}]</span>
                    <span className="text-indigo-400 shrink-0 w-32 truncate">[{log.agent}]</span>
                    <span className="flex-1 text-gray-300">{log.message}</span>
                  </div>
                ))}
                {isExecuting && (
                  <div className="flex gap-2 items-center text-indigo-500/50 mt-4">
                    <span>&gt;</span>
                    <span className="w-2 h-4 bg-indigo-400/50 animate-pulse"></span>
                  </div>
                )}
                {workflowState === 'completed' && (
                  <div className="flex items-center gap-2 text-emerald-400 mt-4 font-bold">
                    <CheckCircle className="w-4 h-4" />
                    Workflow completed successfully.
                  </div>
                )}
                <div ref={logsEndRef} />
              </div>
            </div>
          </MagicCard>
        </MagicGrid>
      </motion.div>

      <motion.section variants={itemVariants} className="grid grid-cols-1 md:grid-cols-3 gap-8 pt-8 border-t border-white/5 relative z-10">
        <CyberCard title={String(totalTraces)} subtitle="Total Tasks" highlight="Live" description="Total sub-tasks completed autonomously." prompt="SYSTEM LOAD CACHE" />
        <CyberCard title={String(escalationCount)} subtitle="Human" highlight="Escalations" description="Manual interventions required." prompt="ACTION REQUIRED" />
        <CyberCard title={workflowState === 'idle' ? '—' : workflowState.toUpperCase()} subtitle="Current" highlight="Status" description="Status from orchestrator." prompt="NEURAL METRIC" />
      </motion.section>

      {/* Onboard Vendor Modal */}
      {showVendorModal && (
        <div className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/90 backdrop-blur-md">
          <div className="bg-[#0a0a0a] border border-white/10 p-8 rounded-2xl w-full max-w-md shadow-2xl relative">
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-xl font-bold text-white uppercase tracking-tight">Onboard Vendor (HITL)</h2>
              <button onClick={() => setShowVendorModal(false)} className="text-gray-500 hover:text-white">
                <X className="w-6 h-6" />
              </button>
            </div>
            <form onSubmit={handleOnboardVendor} className="space-y-6">
              <div>
                <label className="block text-[10px] font-mono text-indigo-400 uppercase tracking-widest mb-2">Vendor ID</label>
                <input 
                  type="text" value={newVendor.vendor_id} onChange={(e) => setNewVendor({...newVendor, vendor_id: e.target.value})}
                  className="w-full bg-black border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500" required
                />
              </div>
              <div>
                <label className="block text-[10px] font-mono text-indigo-400 uppercase tracking-widest mb-2">Vendor Name</label>
                <input 
                  type="text" value={newVendor.name} onChange={(e) => setNewVendor({...newVendor, name: e.target.value})}
                  className="w-full bg-black border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500" required
                />
              </div>
              {vendorError && <p className="text-red-400 text-xs font-mono">{vendorError}</p>}
              <button 
                type="submit" disabled={isSubmittingVendor}
                className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-4 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2"
              >
                {isSubmittingVendor ? <Loader2 className="w-5 h-5 animate-spin" /> : <Plus className="w-5 h-5" />}
                ADD VENDOR & RESUME
              </button>
            </form>
          </div>
        </div>
      )}

      {/* Briefing Email Modal */}
      <AnimatePresence>
        {showBriefingModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.95, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.95, opacity: 0, y: 20 }}
              transition={{ type: "spring", stiffness: 300, damping: 30 }}
              className="bg-black border border-indigo-500/30 rounded-2xl shadow-[0_0_50px_rgba(99,102,241,0.2)] w-full max-w-md overflow-hidden"
            >
              <div className="p-6 border-b border-white/10 flex justify-between items-center bg-indigo-500/5">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 rounded-lg bg-indigo-500/20 flex items-center justify-center">
                    <Sparkles className="w-4 h-4 text-indigo-400" />
                  </div>
                  <h3 className="text-lg font-bold text-white tracking-tight">Generate Briefing</h3>
                </div>
                <button 
                  onClick={() => setShowBriefingModal(false)}
                  className="p-2 hover:bg-white/10 rounded-lg transition-colors"
                >
                  <X className="w-5 h-5 text-gray-400" />
                </button>
              </div>
              
              <form onSubmit={handleGenerateBriefing} className="p-6 space-y-6">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Recipient Email (Optional)</label>
                  <input
                    type="email"
                    value={briefingEmail}
                    onChange={(e) => setBriefingEmail(e.target.value)}
                    placeholder="operator@auditpilot.ai"
                    className="w-full bg-black border border-white/10 rounded-xl px-4 py-3 text-white focus:outline-none focus:border-indigo-500 transition-colors"
                  />
                  <p className="mt-2 text-xs text-gray-500 font-mono">
                    A copy of the system briefing will be dispatched to this address.
                  </p>
                </div>
                
                <button 
                  type="submit"
                  className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-3 rounded-xl shadow-lg transition-all flex items-center justify-center gap-2"
                >
                  <Send className="w-4 h-4" />
                  INITIATE SYNTHESIS
                </button>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Workflow Completion Result Modal */}
      {createPortal(
        <AnimatePresence>
          {showResultModal && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-black/90 backdrop-blur-md"
            >
              <motion.div
                initial={{ scale: 0.9, opacity: 0, y: 30 }}
                animate={{ scale: 1, opacity: 1, y: 0 }}
                exit={{ scale: 0.9, opacity: 0, y: 30 }}
                className="bg-[#0a0a0a] border border-emerald-500/30 rounded-3xl w-full max-w-2xl overflow-hidden shadow-[0_0_100px_rgba(16,185,129,0.15)]"
              >
                {/* Header */}
                <div className="p-8 border-b border-white/10 bg-emerald-500/5 flex justify-between items-center relative overflow-hidden">
                  <div className="absolute top-0 right-0 w-32 h-32 bg-emerald-500/10 blur-[60px] rounded-full -mr-16 -mt-16"></div>
                  <div className="flex items-center gap-5 relative z-10">
                    <div className="w-14 h-14 rounded-2xl bg-emerald-500/20 border border-emerald-500/40 flex items-center justify-center shadow-[0_0_30px_rgba(16,185,129,0.2)]">
                      <CheckCircle className="w-8 h-8 text-emerald-400" />
                    </div>
                    <div>
                      <h3 className="text-2xl font-black text-white tracking-tight uppercase">Workflow Complete</h3>
                      <p className="text-xs font-mono text-emerald-400 uppercase tracking-widest mt-1">Status: Success & Assigned</p>
                    </div>
                  </div>
                  <button 
                    onClick={() => setShowResultModal(false)}
                    className="p-3 hover:bg-white/10 rounded-xl transition-all border border-transparent hover:border-white/10 group"
                  >
                    <X className="w-6 h-6 text-gray-400 group-hover:text-white transition-colors" />
                  </button>
                </div>
                
                <div className="p-8 space-y-8 max-h-[70vh] overflow-y-auto custom-scrollbar">
                  {/* AI Summary Section */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <Sparkles className="w-4 h-4 text-indigo-400" />
                      <span className="text-[10px] font-mono text-indigo-400 uppercase tracking-[0.2em] font-bold">Executive Summary</span>
                    </div>
                    <div className="bg-white/[0.03] border border-white/5 p-8 rounded-2xl relative group overflow-hidden shadow-[inset_0_0_50px_rgba(99,102,241,0.05)]">
                      <div className="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent animate-scan" />
                      <div className="absolute -left-1 top-6 bottom-6 w-1 bg-indigo-500/50 rounded-full group-hover:bg-indigo-400 transition-colors"></div>
                      <div className="relative z-10 transition-all duration-700">
                        <MarkdownRenderer content={workflowSummary || "The workflow has been processed successfully. All tasks have been verified and assigned to the respective team members."} />
                      </div>
                    </div>
                  </div>

                  {/* Technical Execution Logs */}
                  <div className="space-y-4">
                    <div className="flex items-center gap-2">
                      <TerminalIcon className="w-4 h-4 text-emerald-400/50" />
                      <span className="text-[10px] font-mono text-emerald-400/50 uppercase tracking-[0.2em] font-bold">Execution Trace</span>
                    </div>
                    <div className="bg-black border border-white/5 rounded-xl p-4 font-mono text-[11px] space-y-2 overflow-x-hidden">
                      {logs.map((log, i) => (
                        <div key={`modal-log-${i}`} className="flex gap-3 opacity-70 hover:opacity-100 transition-opacity">
                          <span className="text-gray-600 shrink-0">[{log.timestamp}]</span>
                          <span className="text-indigo-400 shrink-0 w-24 truncate">[{log.agent}]</span>
                          <span className="flex-1 text-gray-400">{log.message}</span>
                          <span className="text-emerald-500/50">[OK]</span>
                        </div>
                      ))}
                      <div className="flex gap-3 text-emerald-400 font-bold pt-2 border-t border-white/5 mt-2">
                        <span className="shrink-0">[RESULT]</span>
                        <span className="flex-1 uppercase tracking-widest">Orchestrator: Phase Finalized</span>
                      </div>
                    </div>
                  </div>

                  <div className="pt-4 flex gap-4">
                    <button 
                      onClick={() => setShowResultModal(false)}
                      className="flex-1 bg-white/5 hover:bg-white/10 text-white font-bold py-4 rounded-xl border border-white/10 transition-all uppercase text-xs tracking-widest"
                    >
                      Dismiss
                    </button>
                    <button 
                      onClick={() => {
                          setShowResultModal(false);
                      }}
                      className="flex-1 bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-4 rounded-xl shadow-[0_0_30px_rgba(99,102,241,0.3)] transition-all uppercase text-xs tracking-widest flex items-center justify-center gap-2"
                    >
                      View in Audits
                      <ChevronRight className="w-4 h-4" />
                    </button>
                  </div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </AnimatePresence>,
        document.body
      )}
    </motion.div>
  );
}
