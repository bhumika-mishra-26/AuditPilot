import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { ClipboardCheck, AlertTriangle, ShieldAlert, ArrowRight, Loader2, RefreshCw } from 'lucide-react';
import { getTraces } from '../../lib/api';
import TiltedCard from '../ui/TiltedCard';
import { staggerContainer, itemVariants, cardVariants } from '../ui/PageTransition';

// Animated counter component
function AnimatedCounter({ value, className }: { value: string | number; className?: string }) {
  return (
    <motion.span
      key={String(value)}
      initial={{ opacity: 0, y: -10, scale: 0.8 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: 'spring', stiffness: 300 }}
      className={className}
    >
      {value}
    </motion.span>
  );
}

export default function AuditsScreen() {
  const [escalated, setEscalated] = useState<any[]>([]);
  const [failed, setFailed] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAudits = async () => {
    setLoading(true);
    try {
      const [escData, fData] = await Promise.all([
        getTraces(undefined, 'escalated', 20),
        getTraces(undefined, 'failed', 20)
      ]);
      const uniqueEsc = Array.from(new Map(escData.map(item => [item.workflow_id, item])).values());
      const uniqueFail = Array.from(new Map(fData.map(item => [item.workflow_id, item])).values());
      setEscalated(uniqueEsc);
      setFailed(uniqueFail);
    } catch (err) {
      console.error('Failed to fetch audits:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchAudits(); }, []);

  const statCards = [
    {
      icon: AlertTriangle,
      value: loading ? '—' : escalated.length,
      label: 'Pending Reviews',
      bg: 'bg-indigo-500/10',
      border: 'border-indigo-500/20',
      text: 'text-indigo-400',
      glow: 'rgba(249,115,22,0.15)',
      glowFull: '0 0 40px rgba(249,115,22,0.1)',
    },
    {
      icon: ShieldAlert,
      value: loading ? '—' : failed.length,
      label: 'Critical Failures',
      bg: 'bg-red-500/10',
      border: 'border-red-500/20',
      text: 'text-red-400',
      glow: 'rgba(239,68,68,0.15)',
      glowFull: '0 0 40px rgba(239,68,68,0.1)',
    },
    {
      icon: ClipboardCheck,
      value: '100%',
      label: 'SLA Compliance',
      bg: 'bg-indigo-500/10',
      border: 'border-indigo-500/20',
      text: 'text-indigo-400',
      glow: 'rgba(99,102,241,0.15)',
      glowFull: '0 0 40px rgba(99,102,241,0.1)',
    },
  ];

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
          <h1 className="text-3xl font-black font-heading text-white uppercase tracking-tight">Audit Queue</h1>
          <p className="text-gray-500 text-xs font-mono mt-1 uppercase tracking-widest">
            Workflows requiring human intervention
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.04 }}
          whileTap={{ scale: 0.97 }}
          onClick={fetchAudits}
          className="flex items-center gap-2 px-4 py-2.5 bg-white/5 hover:bg-white/10 border border-white/10 rounded-xl text-gray-300 text-xs font-mono uppercase tracking-wider transition-all"
        >
          <motion.div animate={loading ? { rotate: 360 } : {}} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
            <RefreshCw className="w-3 h-3" />
          </motion.div>
          Refresh Queue
        </motion.button>
      </motion.div>

      {/* Stat Cards */}
      <motion.div variants={staggerContainer} className="flex items-center gap-4">
        {statCards.map((card, i) => {
          const Icon = card.icon;
          return (
            <motion.div
              key={i}
              variants={cardVariants}
              whileHover={{ y: -4, boxShadow: card.glowFull, scale: 1.02 }}
              className={`flex-1 ${card.bg} border ${card.border} rounded-2xl p-6 flex flex-col justify-center relative overflow-hidden cursor-default`}
              transition={{ type: 'spring', stiffness: 300 }}
            >
              <div className={`absolute top-0 right-0 w-32 h-32 blur-3xl rounded-full opacity-40`}
                style={{ background: `radial-gradient(circle, ${card.glow}, transparent)` }}
              />
              <motion.div whileHover={{ scale: 1.15, rotate: 10 }} transition={{ type: 'spring', stiffness: 300 }}>
                <Icon className={`w-8 h-8 ${card.text} mb-2 relative z-10`} />
              </motion.div>
              <h2 className={`text-3xl font-black text-white relative z-10`}>
                <AnimatedCounter value={card.value} />
              </h2>
              <p className={`text-[10px] uppercase tracking-widest font-mono ${card.text} font-bold mt-1 relative z-10`}>
                {card.label}
              </p>
            </motion.div>
          );
        })}
      </motion.div>

      {loading ? (
        <div className="flex flex-col items-center justify-center py-24 text-indigo-400">
          <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}>
            <Loader2 className="w-8 h-8 mb-4" />
          </motion.div>
          <p className="font-mono text-xs uppercase tracking-widest">Scanning queues...</p>
        </div>
      ) : (
        <motion.div
          variants={staggerContainer}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6"
        >
          {escalated.map((trace, i) => (
            <motion.div
              key={trace.id + 'esc'}
              variants={cardVariants}
              whileHover={{ y: -6, scale: 1.02, boxShadow: '0 8px 30px rgba(249,115,22,0.2)' }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            >
              <TiltedCard className="h-[220px] bg-gradient-to-br from-indigo-500/15 to-black/80 flex flex-col justify-between border-indigo-500/20 p-5 rounded-[15px]">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="bg-indigo-500/20 text-indigo-400 text-[9px] font-mono px-2 py-1 rounded border border-indigo-500/30 font-bold uppercase tracking-widest">
                      Pending Review
                    </span>
                    <motion.div animate={{ rotate: [0, 10, -10, 0] }} transition={{ duration: 2, repeat: Infinity }}>
                      <AlertTriangle className="w-4 h-4 text-indigo-400" />
                    </motion.div>
                  </div>
                  <h3 className="text-white font-bold text-sm tracking-wide leading-tight mt-3">Node: {trace.agent}</h3>
                  <p className="text-[10px] text-gray-400 font-mono mt-1 break-all line-clamp-2">{trace.workflow_id}</p>
                </div>
                <div>
                  <p className="text-xs text-indigo-300 line-clamp-2">
                    {trace.decision_reason || trace.error_type || 'Human input required to proceed.'}
                  </p>
                  <motion.button
                    whileHover={{ x: 4, color: '#fb923c' }}
                    className="flex items-center gap-2 mt-4 text-[10px] text-white uppercase font-bold tracking-wider transition-colors"
                  >
                    Review Now <ArrowRight className="w-3 h-3" />
                  </motion.button>
                </div>
              </TiltedCard>
            </motion.div>
          ))}

          {failed.map((trace, i) => (
            <motion.div
              key={trace.id + 'fail'}
              variants={cardVariants}
              whileHover={{ y: -6, scale: 1.02, boxShadow: '0 8px 30px rgba(239,68,68,0.2)' }}
              transition={{ type: 'spring', stiffness: 300, damping: 25 }}
            >
              <TiltedCard className="h-[220px] bg-gradient-to-br from-red-500/15 to-black/80 flex flex-col justify-between border-red-500/20 p-5 rounded-[15px]">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="bg-red-500/20 text-red-400 text-[9px] font-mono px-2 py-1 rounded border border-red-500/30 font-bold uppercase tracking-widest">
                      Critical Failure
                    </span>
                    <ShieldAlert className="w-4 h-4 text-red-400" />
                  </div>
                  <h3 className="text-white font-bold text-sm tracking-wide leading-tight mt-3">
                    {trace.error_type || 'Unknown Error'}
                  </h3>
                  <p className="text-[10px] text-gray-400 font-mono mt-1 break-all line-clamp-2">{trace.workflow_id}</p>
                </div>
                <div>
                  <p className="text-xs text-red-300 line-clamp-2">
                    {trace.decision_reason || 'Process terminated unexpectedly.'}
                  </p>
                  <motion.button
                    whileHover={{ x: 4, color: '#f87171' }}
                    className="flex items-center gap-2 mt-4 text-[10px] text-white uppercase font-bold tracking-wider"
                  >
                    Investigate <ArrowRight className="w-3 h-3" />
                  </motion.button>
                </div>
              </TiltedCard>
            </motion.div>
          ))}

          {escalated.length === 0 && failed.length === 0 && !loading && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="col-span-full py-24 flex flex-col items-center justify-center opacity-40"
            >
              <motion.div
                animate={{ scale: [1, 1.05, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              >
                <ClipboardCheck className="w-14 h-14 text-gray-500 mb-4" />
              </motion.div>
              <p className="text-lg font-bold text-gray-400 tracking-wider">NO PENDING AUDITS</p>
              <p className="text-xs font-mono text-gray-500 mt-2 uppercase tracking-widest">
                All workflows are running optimally
              </p>
            </motion.div>
          )}
        </motion.div>
      )}
    </motion.div>
  );
}
