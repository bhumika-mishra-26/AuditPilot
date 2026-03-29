import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { RefreshCw, BrainCircuit, Activity, Database, AlertCircle, Search, Brain, ShieldAlert } from 'lucide-react';
import { getTraces, getPatternMemory } from '../../lib/api';
import { MagicGrid, MagicCard } from '../ui/MagicBento';
import { staggerContainer, itemVariants, cardVariants } from '../ui/PageTransition';

export default function AnalyticsScreen() {
  const [traces, setTraces] = useState<any[]>([]);
  const [memory, setMemory] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    setLoading(true);
    try {
      const [tData, mData] = await Promise.all([
        getTraces(undefined, undefined, 50),
        getPatternMemory()
      ]);
      setTraces(tData);
      setMemory(mData);
    } catch (err) {
      console.error('Failed to fetch analytics:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchData(); }, []);

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
          <h1 className="text-3xl font-black font-heading text-white uppercase tracking-tight">
            Intelligence Analytics
          </h1>
          <p className="text-gray-500 text-xs font-mono mt-1 uppercase tracking-widest">
            System memory and trace execution logs
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.04, boxShadow: '0 0 20px rgba(99,102,241,0.3)' }}
          whileTap={{ scale: 0.97 }}
          onClick={fetchData}
          className="flex items-center gap-2 px-4 py-2.5 bg-indigo-500/10 hover:bg-indigo-500/20 border border-indigo-500/30 rounded-xl text-indigo-300 text-xs font-mono uppercase tracking-wider transition-all"
        >
          <motion.div animate={loading ? { rotate: 360 } : {}} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
            <RefreshCw className="w-3 h-3" />
          </motion.div>
          Sync Data
        </motion.button>
      </motion.div>

      <MagicGrid className="lg:grid-cols-4 gap-6">
        {/* System Memory / W4 Logic */}
        <MagicCard className="lg:col-span-2 h-[600px] bg-black/40 border border-indigo-500/20" contentClassName="flex flex-col" gradientColor="#6366f1">
          <div className="px-6 py-4 border-b border-white/5 flex items-center justify-between flex-shrink-0">
            <div className="flex items-center gap-2">
              <BrainCircuit className="w-4 h-4 text-indigo-400" />
              <h2 className="text-sm font-bold text-gray-300 uppercase tracking-widest">W4 Pattern Memory</h2>
            </div>
            <motion.span
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: 'spring', stiffness: 300 }}
              className="px-2 py-0.5 rounded-full bg-indigo-500/10 text-indigo-400 text-[10px] font-mono border border-indigo-500/20"
            >
              {memory.length} Patterns
            </motion.span>
          </div>
          <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-4">
            {memory.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-600">
                <Brain className="w-8 h-8 opacity-20 mb-2" />
                <p className="text-xs font-mono uppercase">Memory Banks Empty</p>
              </div>
            ) : (
              <motion.div variants={staggerContainer} initial="initial" animate="animate" className="space-y-4">
                {memory.map((mem, i) => (
                  <motion.div
                    key={mem.error_hash + i}
                    variants={cardVariants}
                    whileHover={{ y: -2, borderColor: 'rgba(99,102,241,0.3)', boxShadow: '0 4px 20px rgba(99,102,241,0.1)' }}
                    className="bg-black/60 border border-white/10 rounded-xl p-4 transition-colors cursor-default"
                  >
                    <div className="flex items-start justify-between mb-3">
                      <div>
                        <h3 className="text-indigo-300 text-xs font-bold font-mono uppercase">{mem.error_type}</h3>
                        <p className="text-white text-sm font-bold mt-1 max-w-[200px] truncate" title={mem.error_hash}>
                          {mem.error_hash}
                        </p>
                      </div>
                      {mem.is_systemic === 1 && (
                        <motion.span
                          initial={{ scale: 0 }}
                          animate={{ scale: 1 }}
                          className="flex items-center gap-1 text-[10px] font-bold uppercase text-red-400 bg-red-500/10 border border-red-500/20 px-2 py-1 rounded"
                        >
                          <ShieldAlert className="w-3 h-3" /> Systemic
                        </motion.span>
                      )}
                    </div>
                    <div className="grid grid-cols-2 gap-2">
                      <div className="bg-white/5 rounded-lg p-2 border border-white/5">
                        <p className="text-[9px] text-gray-500 uppercase tracking-widest font-mono mb-1">Occurrences</p>
                        <p className="text-white font-bold">{mem.count}</p>
                      </div>
                      <div className="bg-white/5 rounded-lg p-2 border border-white/5">
                        <p className="text-[9px] text-gray-500 uppercase tracking-widest font-mono mb-1">Success Rate</p>
                        <p className="text-white font-bold">{mem.success_rate?.toFixed(2) || '0.00'}</p>
                      </div>
                    </div>
                  </motion.div>
                ))}
              </motion.div>
            )}
          </div>
        </MagicCard>

        {/* Live Traces */}
        <MagicCard className="lg:col-span-2 h-[600px] bg-black/40 border border-emerald-500/20" contentClassName="flex flex-col" gradientColor="#10b981">
          <div className="px-6 py-4 border-b border-white/5 flex flex-col gap-3 flex-shrink-0">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Activity className="w-4 h-4 text-emerald-400" />
                <h2 className="text-sm font-bold text-gray-300 uppercase tracking-widest">Audit Traces</h2>
              </div>
              <motion.span
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 2, repeat: Infinity }}
                className="px-2 py-0.5 rounded-full bg-emerald-500/10 text-emerald-400 text-[10px] font-mono border border-emerald-500/20"
              >
                Live
              </motion.span>
            </div>
            <div className="relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3 h-3 text-gray-500" />
              <input
                type="text"
                placeholder="Filter by hash, step, or status..."
                className="w-full bg-black/50 border border-white/10 rounded-lg py-1.5 pl-8 pr-3 text-xs text-white placeholder:text-gray-600 focus:outline-none focus:border-emerald-500/50 focus:ring-1 focus:ring-emerald-500/30 transition-all font-mono"
              />
            </div>
          </div>

          <div className="flex-1 overflow-y-auto custom-scrollbar p-6 space-y-3">
            {traces.length === 0 ? (
              <div className="h-full flex flex-col items-center justify-center text-gray-600">
                <Database className="w-8 h-8 opacity-20 mb-2" />
                <p className="text-xs font-mono uppercase">Awaiting trace data</p>
              </div>
            ) : (
              <motion.div variants={staggerContainer} initial="initial" animate="animate" className="space-y-3">
                {traces.map((trace, i) => (
                  <motion.div
                    key={trace.id + i}
                    variants={cardVariants}
                    whileHover={{ x: 4, backgroundColor: 'rgba(255,255,255,0.08)' }}
                    className="flex flex-col gap-2 p-3 bg-white/5 border border-white/5 rounded-xl cursor-default"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <motion.span
                          animate={trace.status === 'success' ? {} : { opacity: [0.4, 1, 0.4] }}
                          transition={{ duration: 1.5, repeat: Infinity }}
                          className={`w-1.5 h-1.5 rounded-full ${trace.status === 'success' ? 'bg-emerald-400' : trace.status === 'escalated' ? 'bg-indigo-400' : 'bg-red-400'}`}
                        />
                        <span className="text-xs font-bold text-gray-300">
                          {trace.step_id} <span className="text-gray-600 font-normal">[{trace.agent}]</span>
                        </span>
                      </div>
                      <span className="text-[9px] font-mono text-gray-500">
                        {new Date(trace.created_at).toLocaleTimeString()}
                      </span>
                    </div>
                    {trace.log_message && (
                      <p className="text-[11px] text-gray-400 pl-3.5 leading-relaxed">{trace.log_message}</p>
                    )}
                    {trace.error_type && (
                      <div className="ml-3.5 p-2 bg-red-500/5 border border-red-500/10 rounded-lg flex items-start gap-2 mt-1">
                        <AlertCircle className="w-3 h-3 text-red-400 flex-shrink-0 mt-0.5" />
                        <div>
                          <p className="text-[10px] uppercase font-bold text-red-400 font-mono tracking-wider">{trace.error_type}</p>
                          {trace.decision_reason && (
                            <p className="text-[10px] text-red-300/70 mt-0.5">{trace.decision_reason}</p>
                          )}
                        </div>
                      </div>
                    )}
                  </motion.div>
                ))}
              </motion.div>
            )}
          </div>
        </MagicCard>
      </MagicGrid>
    </motion.div>
  );
}
