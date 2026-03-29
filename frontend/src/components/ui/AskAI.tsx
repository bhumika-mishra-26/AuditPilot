import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Sparkles, X, Send, ChevronRight, Loader2, Bot, MessageSquare } from 'lucide-react';
import MarkdownRenderer from '../ui/MarkdownRenderer';
import { explainWorkflow } from '../../lib/api';

interface AskAIProps {
  workflowId: string | null;
}

const PREDEFINED_PROMPTS = [
  "What happened in this workflow?",
  "Why was the owner resolution escalated?",
  "Explain the HITL escalation process",
  "What agents were involved and what did each do?",
  "Were there any errors or failures?",
  "Summarize the workflow outcome",
];

export default function AskAI({ workflowId }: AskAIProps) {
  const [isOpen, setIsOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [response, setResponse] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [hasAsked, setHasAsked] = useState(false);
  const responseRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  useEffect(() => {
    if (responseRef.current) {
      responseRef.current.scrollTop = responseRef.current.scrollHeight;
    }
  }, [response]);

  const handleAsk = async (question: string) => {
    if (!question.trim() || isLoading) return;

    setIsLoading(true);
    setResponse('');
    setHasAsked(true);
    setQuery('');

    try {
      if (!workflowId) {
        // No workflow running – give a helpful static response
        setResponse(`### No Active Workflow

There is no active workflow to analyze right now. Please run a workflow first using the **Intelligence Engine Interface** above, then come back to ask me about it.

---

**Tip:** Try running a query like:
- "Onboard Acme Corp with email acme@corp.com"
- "Process meeting notes for Q4 review"
- "Handle invoice from vendor V-101"`);
        setIsLoading(false);
        return;
      }

      const res = await explainWorkflow(workflowId, question);

      if (!res.ok) {
        const err = await res.text();
        setResponse(`### ⚠️ Error\n\n${err || 'Failed to get explanation from backend.'}`);
        setIsLoading(false);
        return;
      }

      // Stream the response
      const reader = res.body?.getReader();
      const decoder = new TextDecoder();

      if (!reader) {
        setResponse('Failed to read streaming response.');
        setIsLoading(false);
        return;
      }

      let accumulated = '';
      while (true) {
        const { done, value } = await reader.read();
        if (done) break;
        const chunk = decoder.decode(value, { stream: true });
        accumulated += chunk;
        setResponse(accumulated);
      }
    } catch (err: any) {
      setResponse(`### ⚠️ Connection Error\n\nCould not reach the AuditPilot backend.\n\n\`${err.message}\``);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    handleAsk(query);
  };

  return (
    <>
      {/* Floating Button */}
      <AnimatePresence>
        {!isOpen && (
          <motion.button
            initial={{ scale: 0, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0, opacity: 0 }}
            transition={{ type: 'spring', stiffness: 400, damping: 25 }}
            onClick={() => setIsOpen(true)}
            className="fixed bottom-8 right-8 z-50 group"
          >
            <div className="relative">
              {/* Glow ring */}
              <motion.div
                animate={{ scale: [1, 1.2, 1], opacity: [0.3, 0.6, 0.3] }}
                transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
                className="absolute inset-0 rounded-full bg-indigo-500/30 blur-md"
              />
              <div className="relative w-14 h-14 rounded-full bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center shadow-[0_0_30px_rgba(99,102,241,0.4)] border border-indigo-400/30 group-hover:shadow-[0_0_50px_rgba(99,102,241,0.6)] transition-shadow overflow-hidden">
                <img src="/ask-ai.png" alt="Ask AI" className="w-9 h-9 object-contain drop-shadow-[0_0_8px_rgba(255,255,255,0.4)]" />
              </div>
            </div>
          </motion.button>
        )}
      </AnimatePresence>

      {/* Modal */}
      <AnimatePresence>
        {isOpen && (
          <motion.div
            initial={{ opacity: 0, y: 40, scale: 0.95 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: 40, scale: 0.95 }}
            transition={{ type: 'spring', stiffness: 350, damping: 30 }}
            className="fixed bottom-8 right-8 z-50 w-[520px] max-h-[80vh] flex flex-col bg-[#0a0a0a]/95 backdrop-blur-2xl border border-white/10 rounded-2xl shadow-[0_0_80px_rgba(99,102,241,0.15)] overflow-hidden"
          >
            {/* Header */}
            <div className="px-6 py-4 border-b border-white/10 bg-indigo-500/5 flex items-center justify-between shrink-0">
              <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-600 to-violet-600 flex items-center justify-center shadow-[0_0_15px_rgba(99,102,241,0.3)] overflow-hidden">
                  <img src="/ask-ai.png" alt="Ask AI" className="w-6 h-6 object-contain" />
                </div>
                <div>
                  <h3 className="text-sm font-bold text-white tracking-tight">Ask AI</h3>
                  <p className="text-[9px] font-mono text-indigo-400 uppercase tracking-[0.15em]">
                    {workflowId ? `Workflow: ${workflowId.slice(0, 8)}...` : 'Neural Analysis Engine'}
                  </p>
                </div>
              </div>
              <button
                onClick={() => setIsOpen(false)}
                className="p-2 hover:bg-white/10 rounded-lg transition-colors"
              >
                <X className="w-4 h-4 text-gray-400" />
              </button>
            </div>

            {/* Content */}
            <div ref={responseRef} className="flex-1 overflow-y-auto custom-scrollbar p-5 min-h-[200px] max-h-[50vh]">
              {!hasAsked ? (
                <div className="space-y-4">
                  <div className="text-center mb-6">
                    <motion.div
                      animate={{ scale: [1, 1.05, 1] }}
                      transition={{ duration: 4, repeat: Infinity, ease: 'easeInOut' }}
                      className="w-12 h-12 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center mx-auto mb-3"
                    >
                      <MessageSquare className="w-6 h-6 text-indigo-400" />
                    </motion.div>
                    <p className="text-xs text-gray-400 font-mono uppercase tracking-widest">Choose a prompt or type your own</p>
                  </div>
                  <div className="space-y-2">
                    {PREDEFINED_PROMPTS.map((prompt, idx) => (
                      <motion.button
                        key={idx}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                        transition={{ delay: idx * 0.06 }}
                        onClick={() => handleAsk(prompt)}
                        className="w-full text-left px-4 py-3 rounded-xl bg-white/[0.03] hover:bg-indigo-500/10 border border-white/5 hover:border-indigo-500/20 text-sm text-gray-300 hover:text-white transition-all group flex items-center justify-between"
                      >
                        <span>{prompt}</span>
                        <ChevronRight className="w-4 h-4 text-gray-600 group-hover:text-indigo-400 transition-colors" />
                      </motion.button>
                    ))}
                  </div>
                </div>
              ) : (
                <div>
                  {isLoading && !response && (
                    <div className="flex flex-col items-center justify-center py-12 gap-4">
                      <motion.div
                        animate={{ rotate: 360 }}
                        transition={{ duration: 2, repeat: Infinity, ease: 'linear' }}
                      >
                        <Loader2 className="w-8 h-8 text-indigo-400" />
                      </motion.div>
                      <p className="text-xs text-indigo-400 font-mono uppercase tracking-widest">Analyzing workflow traces...</p>
                    </div>
                  )}
                  {response && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                    >
                      <MarkdownRenderer content={response} />
                      {isLoading && (
                        <motion.span
                          animate={{ opacity: [1, 0, 1] }}
                          transition={{ duration: 0.8, repeat: Infinity }}
                          className="inline-block w-2 h-4 bg-indigo-400/60 ml-1 align-middle"
                        />
                      )}
                    </motion.div>
                  )}
                </div>
              )}
            </div>

            {/* Input */}
            <div className="p-4 border-t border-white/10 bg-black/40 shrink-0">
              {hasAsked && (
                <button
                  onClick={() => { setHasAsked(false); setResponse(''); }}
                  className="w-full mb-3 text-[10px] font-mono text-indigo-400 hover:text-indigo-300 uppercase tracking-widest text-center transition-colors"
                >
                  ← Back to prompts
                </button>
              )}
              <form onSubmit={handleSubmit} className="flex gap-2">
                <input
                  ref={inputRef}
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder="Ask anything about this workflow..."
                  className="flex-1 bg-white/[0.04] border border-white/10 rounded-xl px-4 py-2.5 text-sm text-white placeholder:text-gray-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/20 transition-all font-mono"
                  disabled={isLoading}
                />
                <button
                  type="submit"
                  disabled={!query.trim() || isLoading}
                  className="px-4 py-2.5 bg-indigo-600 hover:bg-indigo-500 disabled:bg-white/5 disabled:text-gray-600 text-white rounded-xl transition-colors flex items-center gap-1"
                >
                  {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
                </button>
              </form>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}
