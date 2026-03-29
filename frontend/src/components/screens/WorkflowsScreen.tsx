import React, { useState, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { RefreshCw, ChevronRight, AlertTriangle, CheckCircle, XCircle, Loader2, Clock, Send, Sparkles, MessageSquare, User } from 'lucide-react';
import { listWorkflows, getWorkflowStatus, resumeWorkflow, explainWorkflow, type WorkflowListItem, type WorkflowStatusResponse } from '../../lib/api';
import { MagicGrid, MagicCard } from '../ui/MagicBento';
import { staggerContainer, itemVariants, cardVariants } from '../ui/PageTransition';
import MarkdownRenderer from '../ui/MarkdownRenderer';
import AskAI from '../ui/AskAI';

const statusIcon = (status: string) => {
  switch (status) {
    case 'completed': return <CheckCircle className="w-4 h-4 text-emerald-400" />;
    case 'failed': return <XCircle className="w-4 h-4 text-red-400" />;
    case 'escalated': return <AlertTriangle className="w-4 h-4 text-indigo-400" />;
    case 'running': return <Loader2 className="w-4 h-4 text-indigo-400 animate-spin" />;
    default: return <Clock className="w-4 h-4 text-gray-400" />;
  }
};

const statusBadge = (status: string) => {
  const colors: Record<string, string> = {
    completed: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30',
    failed: 'bg-red-500/10 text-red-400 border-red-500/30',
    escalated: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
    running: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/30',
  };
  return `${colors[status] || 'bg-white/5 text-gray-400 border-white/10'} px-3 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider border`;
};

export default function WorkflowsScreen() {
  const [workflows, setWorkflows] = useState<WorkflowListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [detail, setDetail] = useState<WorkflowStatusResponse | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [hitlInput, setHitlInput] = useState('');
  const [isResuming, setIsResuming] = useState(false);

  const fetchWorkflows = useCallback(async () => {
    try {
      const data = await listWorkflows(50);
      setWorkflows(data);
    } catch (err) {
      console.error('Failed to fetch workflows:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchWorkflows(); }, [fetchWorkflows]);

  const openDetail = async (wfId: string) => {
    setSelectedId(wfId);
    setDetailLoading(true);
    setDetail(null);
    try {
      const data = await getWorkflowStatus(wfId);
      setDetail(data);
    } catch (err) {
      console.error('Failed to fetch workflow details:', err);
    } finally {
      setDetailLoading(false);
    }
  };

  const handleResume = async (input: string) => {
    if (!selectedId || !input.trim()) return;
    setIsResuming(true);
    try {
      await resumeWorkflow(selectedId, input.trim());
      setHitlInput('');
      
      // Poll for completion — the backend runs W3 async which may take
      // several seconds (especially if LLM extraction is involved).
      const pollId = selectedId;
      let attempts = 0;
      const maxAttempts = 15; // 15 * 2s = 30s max
      const poll = async () => {
        attempts++;
        const data = await getWorkflowStatus(pollId);
        setDetail(data);
        if (data.state === 'running' && attempts < maxAttempts) {
          setTimeout(poll, 2000);
        } else {
          fetchWorkflows();
          setIsResuming(false);
        }
      };
      setTimeout(poll, 2000);
      
    } catch (err) {
      console.error('Resume failed:', err);
      setIsResuming(false);
    }
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="initial"
      animate="animate"
      className="space-y-8 pb-20"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black font-heading text-white uppercase tracking-tight">Workflow History</h1>
          <p className="text-gray-500 text-xs font-mono mt-1 uppercase tracking-widest">All orchestrated workflow executions</p>
        </div>
        <motion.button
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.97 }}
          onClick={() => { setLoading(true); fetchWorkflows(); }}
          className="flex items-center gap-2 px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-gray-300 text-xs font-mono uppercase tracking-wider transition-colors"
        >
          <motion.div animate={loading ? { rotate: 360 } : {}} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
            <RefreshCw className="w-3 h-3" />
          </motion.div>
          Refresh
        </motion.button>
      </motion.div>

      <MagicGrid className="lg:grid-cols-5 gap-8">
        {/* Workflow List */}
        <MagicCard className="lg:col-span-2 h-[750px] bg-black/40 border border-white/10" contentClassName="flex flex-col" gradientColor="#6366f1">
          <div className="px-6 py-4 border-b border-white/5 flex-shrink-0">
            <h2 className="text-sm font-bold text-gray-400 uppercase tracking-widest">{workflows.length} Workflows</h2>
          </div>
          <div className="flex-1 overflow-y-auto custom-scrollbar divide-y divide-white/5">
            {loading && (
              <div className="flex items-center justify-center py-20 text-gray-500">
                <Loader2 className="w-6 h-6 animate-spin" />
              </div>
            )}
            {!loading && workflows.length === 0 && (
              <div className="flex items-center justify-center py-20 text-gray-600 text-sm">
                No workflows yet. Run one from the Dashboard.
              </div>
            )}
            {workflows.map((wf, idx) => (
              <motion.button
                key={wf.workflow_id}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: idx * 0.03, duration: 0.3 }}
                whileHover={{ backgroundColor: 'rgba(255,255,255,0.05)', x: 2 }}
                onClick={() => openDetail(wf.workflow_id)}
                className={`w-full text-left px-6 py-4 flex items-center gap-4 transition-colors ${selectedId === wf.workflow_id ? 'bg-indigo-500/10 border-l-2 border-indigo-500' : ''}`}
              >
                {statusIcon(wf.status)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="text-white text-sm font-bold truncate">{wf.workflow_type}</span>
                    <span className={statusBadge(wf.status)}>{wf.status}</span>
                  </div>
                  <div className="text-[10px] text-gray-500 font-mono mt-1 truncate">{wf.workflow_id}</div>
                  <div className="text-[10px] text-gray-600 font-mono">{new Date(wf.created_at).toLocaleString()}</div>
                </div>
                <motion.div whileHover={{ x: 3 }}>
                  <ChevronRight className="w-4 h-4 text-gray-600 flex-shrink-0" />
                </motion.div>
              </motion.button>
            ))}
          </div>
        </MagicCard>

        {/* Detail Panel */}
        <MagicCard className="lg:col-span-3 h-[750px] bg-black/40 border border-white/10" contentClassName="flex flex-col" gradientColor="#ec4899">
          {!selectedId && (
            <div className="flex items-center justify-center h-full text-gray-600 text-sm py-40">
              Select a workflow to view details
            </div>
          )}

          {selectedId && detailLoading && (
            <div className="flex items-center justify-center h-full py-40">
              <Loader2 className="w-6 h-6 animate-spin text-indigo-400" />
            </div>
          )}

          {detail && (
            <div className="flex flex-col h-full">
              <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between">
                <div>
                  <h2 className="text-sm font-bold text-white uppercase tracking-wider">{detail.type} Workflow</h2>
                  <span className="text-[10px] font-mono text-gray-500">{detail.workflow_id}</span>
                </div>
                <span className={statusBadge(detail.state)}>{detail.state}</span>
              </div>

              {/* AI Summary Section */}
              {detail.summary && (
                <div className="px-6 py-4 border-b border-white/5 bg-indigo-500/5">
                  <div className="flex items-center gap-2 mb-2">
                    <Sparkles className="w-3 h-3 text-indigo-400" />
                    <span className="text-[9px] font-mono text-indigo-400 uppercase tracking-widest font-bold">Executive Summary</span>
                  </div>
                  <div className="bg-black/20 rounded-xl p-4 border border-white/5">
                    <MarkdownRenderer content={detail.summary} />
                  </div>
                </div>
              )}

              {/* Steps */}
              <div className="flex-1 overflow-y-auto custom-scrollbar px-6 py-4 space-y-3">
                {detail.steps.map((step, i) => (
                  <motion.div
                    key={step.step_id}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.03 }}
                    className="flex items-start gap-3 text-xs"
                  >
                    {statusIcon(step.status)}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2">
                        <span className="text-indigo-400 font-bold">[{step.agent}]</span>
                        <span className="text-gray-500">{step.step_id}</span>
                      </div>
                      <p className="text-gray-300 mt-0.5">{step.log_message || step.decision_reason || step.status}</p>
                      {step.error_type && <span className="text-indigo-400 text-[10px]">Error: {step.error_type}</span>}
                    </div>
                  </motion.div>
                ))}
              </div>

              {/* HITL Resume Panel */}
              {detail.state === 'escalated' && detail.hitl_reason && (
                <div className="px-6 py-4 border-t border-indigo-500/20 bg-indigo-500/5">
                  <div className="flex items-start gap-3">
                    <AlertTriangle className="w-5 h-5 text-indigo-400 flex-shrink-0 mt-0.5" />
                    <div className="flex-1">
                      <p className="text-indigo-300 text-sm mb-3">{detail.hitl_reason}</p>
                      {detail.hitl_options.length > 0 && (
                        <div className="flex flex-wrap gap-2 mb-3">
                          {detail.hitl_options.map(opt => (
                            <button
                              key={opt}
                              onClick={() => handleResume(opt)}
                              disabled={isResuming}
                              className="px-3 py-1.5 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 text-indigo-300 rounded-lg text-[10px] font-mono uppercase tracking-wider transition-colors disabled:opacity-50"
                            >
                              {opt.replace(/_/g, ' ')}
                            </button>
                          ))}
                        </div>
                      )}
                      <form onSubmit={(e) => { e.preventDefault(); handleResume(hitlInput); }} className="flex gap-2">
                        <input
                          type="text"
                          value={hitlInput}
                          onChange={(e) => setHitlInput(e.target.value)}
                          placeholder="Or type your response..."
                          className="flex-1 bg-black/50 border border-white/10 rounded-lg px-3 py-1.5 text-xs text-white placeholder:text-gray-600 focus:outline-none focus:border-indigo-500/50"
                          disabled={isResuming}
                        />
                        <button
                          type="submit"
                          disabled={!hitlInput.trim() || isResuming}
                          className="px-3 py-1.5 bg-indigo-500 text-white font-bold rounded-lg text-[10px] uppercase disabled:opacity-50 flex items-center gap-1"
                        >
                          {isResuming ? <Loader2 className="w-3 h-3 animate-spin" /> : <Send className="w-3 h-3" />}
                        </button>
                      </form>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </MagicCard>
      </MagicGrid>

      {/* Floating Ask AI Button */}
      <AskAI workflowId={selectedId} />
    </motion.div>
  );
}
