import React from 'react';
import { motion } from 'motion/react';
import { Settings, User, Bell, Shield, Cloud, Key, FileText, Cpu } from 'lucide-react';
import { staggerContainer, itemVariants, cardVariants } from '../ui/PageTransition';

const settingsGroups = [
  {
    title: 'Intelligence Engine',
    icon: Cpu,
    items: [
      { name: 'Autonomous Decision Masking', type: 'toggle', enabled: true },
      { name: 'W4 Pattern Memory Threshold', type: 'slider', value: '70%' },
      { name: 'LLM Classification Fallback', type: 'toggle', enabled: true },
    ],
  },
  {
    title: 'Security & Access',
    icon: Shield,
    items: [
      { name: 'Enforce Multi-Factor', type: 'toggle', enabled: true },
      { name: 'Session Timeout Reset', type: 'button', value: 'Configure' },
      { name: 'API Rate Limiting', type: 'toggle', enabled: false },
    ],
  },
  {
    title: 'Network Nodes',
    icon: Cloud,
    items: [
      { name: 'Primary Cloud Sync', type: 'status', value: 'Connected' },
      { name: 'Backup Region Replication', type: 'toggle', enabled: true },
      { name: 'Edge Node Validation', type: 'toggle', enabled: false },
    ],
  },
];

function AnimatedToggle({ enabled }: { enabled: boolean }) {
  return (
    <motion.div
      className={`w-10 h-5 rounded-full relative cursor-pointer border ${
        enabled ? 'bg-emerald-500 border-emerald-400/30' : 'bg-gray-700 border-white/10'
      }`}
      whileTap={{ scale: 0.95 }}
    >
      <motion.div
        animate={{ left: enabled ? '22px' : '2px' }}
        transition={{ type: 'spring', stiffness: 500, damping: 30 }}
        className="absolute top-0.5 w-4 h-4 bg-white rounded-full shadow-sm"
      />
      {enabled && (
        <motion.div
          animate={{ opacity: [0.3, 0.7, 0.3] }}
          transition={{ duration: 2, repeat: Infinity }}
          className="absolute inset-0 rounded-full bg-emerald-400/20"
        />
      )}
    </motion.div>
  );
}

export default function SettingsScreen() {
  return (
    <motion.div
      variants={staggerContainer}
      initial="initial"
      animate="animate"
      className="space-y-8 pb-20 relative"
    >
      {/* Background Decor */}
      <div className="absolute top-0 right-0 w-[500px] h-[500px] bg-indigo-500/5 blur-[120px] rounded-full pointer-events-none -z-10" />

      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black font-heading text-white uppercase tracking-tight">
            System Configuration
          </h1>
          <p className="text-gray-500 text-xs font-mono mt-1 uppercase tracking-widest">
            Master parameters and module protocols
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.03, boxShadow: '0 0 25px rgba(99,102,241,0.4)' }}
          whileTap={{ scale: 0.97 }}
          className="px-5 py-2.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl font-bold shadow-[0_0_20px_rgba(99,102,241,0.3)] flex items-center gap-2 group text-sm uppercase tracking-wider"
        >
          <motion.div whileHover={{ rotate: 180 }} transition={{ duration: 0.5 }}>
            <Settings className="w-4 h-4" />
          </motion.div>
          Apply Changes
        </motion.button>
      </motion.div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Left Column */}
        <motion.div variants={staggerContainer} className="space-y-8">
          <motion.div
            variants={cardVariants}
            whileHover={{ y: -4, boxShadow: '0 8px 30px rgba(99,102,241,0.1)' }}
            className="w-full bg-black/40 border border-indigo-500/20 rounded-2xl text-white overflow-hidden"
          >
            <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-indigo-500/30 to-transparent" />
            <div className="p-6 space-y-6">
              <div className="flex items-center gap-4 border-b border-indigo-500/20 pb-6">
                <motion.div
                  whileHover={{ scale: 1.1 }}
                  animate={{ boxShadow: ['0 0 15px rgba(99,102,241,0.2)', '0 0 25px rgba(99,102,241,0.35)', '0 0 15px rgba(99,102,241,0.2)'] }}
                  transition={{ duration: 3, repeat: Infinity }}
                  className="w-16 h-16 rounded-full bg-indigo-500/10 border border-indigo-500/30 flex items-center justify-center"
                >
                  <User className="w-8 h-8 text-indigo-400" />
                </motion.div>
                <div>
                  <h2 className="font-bold text-lg tracking-wide uppercase">System Operator</h2>
                  <p className="text-xs font-mono text-indigo-400 mt-1 uppercase">Control Auth L4 // Admin</p>
                </div>
              </div>

              <div className="space-y-1">
                {[
                  { icon: Key, label: 'API Keys', value: '2 active' },
                  { icon: Bell, label: 'Alert Rules', value: '14 configured' },
                  { icon: FileText, label: 'Audit Logs', value: 'Export', highlight: true },
                ].map(({ icon: Icon, label, value, highlight }, i) => (
                  <motion.div
                    key={i}
                    whileHover={{ x: 4, backgroundColor: 'rgba(255,255,255,0.05)' }}
                    className="flex items-center justify-between group cursor-pointer p-2 rounded-lg transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <Icon className="w-4 h-4 text-gray-400 group-hover:text-white transition-colors" />
                      <span className="text-sm text-gray-300 group-hover:text-white transition-colors">{label}</span>
                    </div>
                    <span className={`text-xs font-mono ${highlight ? 'text-indigo-400' : 'text-gray-500'}`}>{value}</span>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.div>

          <motion.div
            variants={cardVariants}
            whileHover={{ y: -4, boxShadow: '0 8px 40px rgba(239,68,68,0.15)' }}
            className="w-full bg-red-500/10 border border-red-500/20 rounded-2xl p-6 relative overflow-hidden cursor-default"
          >
            <div className="absolute inset-0 bg-gradient-to-br from-red-500/10 to-transparent pointer-events-none" />
            <div className="absolute top-0 right-0 w-48 h-48 bg-red-500/20 blur-3xl rounded-full" />
            <div className="relative z-10">
              <p className="text-[9px] text-red-400 font-mono uppercase tracking-widest mb-2 font-bold">Emergency Protocol</p>
              <h3 className="text-white font-black text-xl uppercase tracking-tight mb-1">STATION OVERRIDE</h3>
              <p className="text-red-300/70 text-xs font-mono">Emergency Protocol Alpha.</p>
              <motion.button
                whileHover={{ scale: 1.04 }}
                whileTap={{ scale: 0.97 }}
                className="mt-4 px-4 py-2 bg-red-500/20 hover:bg-red-500/30 border border-red-500/30 text-red-300 text-[10px] font-mono uppercase tracking-widest rounded-lg transition-all"
              >
                Activate Override
              </motion.button>
            </div>
          </motion.div>
        </motion.div>

        {/* Right Column */}
        <motion.div variants={staggerContainer} className="lg:col-span-2 space-y-6">
          {settingsGroups.map((group, idx) => {
            const Icon = group.icon;
            return (
              <motion.div
                key={idx}
                variants={cardVariants}
                whileHover={{ y: -2 }}
                className="bg-black/40 border border-white/[0.07] rounded-2xl overflow-hidden shadow-[0_4px_30px_rgba(0,0,0,0.4)]"
              >
                <div className="px-6 py-4 border-b border-white/5 bg-white/[0.03] flex items-center gap-3">
                  <Icon className="w-4 h-4 text-indigo-400" />
                  <h3 className="uppercase tracking-widest text-xs font-bold text-gray-300">{group.title}</h3>
                </div>
                <div className="divide-y divide-white/[0.04]">
                  {group.items.map((item, i) => (
                    <motion.div
                      key={i}
                      whileHover={{ backgroundColor: 'rgba(255,255,255,0.03)' }}
                      className="p-6 flex items-center justify-between"
                    >
                      <span className="font-mono text-xs text-gray-400 uppercase tracking-wide">{item.name}</span>

                      {item.type === 'toggle' && (
                        <AnimatedToggle enabled={item.enabled ?? false} />
                      )}

                      {item.type === 'slider' && (
                        <div className="flex items-center gap-4 w-48">
                          <input
                            type="range"
                            min="0"
                            max="100"
                            defaultValue="70"
                            className="w-full accent-indigo-500 h-1 bg-gray-700 rounded-lg appearance-none cursor-pointer"
                          />
                          <span className="font-mono text-[10px] text-indigo-400 font-bold w-8">{item.value}</span>
                        </div>
                      )}

                      {item.type === 'button' && (
                        <motion.button
                          whileHover={{ scale: 1.05, borderColor: 'rgba(99,102,241,0.4)', color: '#a5b4fc' }}
                          whileTap={{ scale: 0.97 }}
                          className="px-3 py-1 bg-white/10 hover:bg-white/15 border border-white/20 rounded-md text-[10px] font-mono uppercase tracking-wider text-gray-300 transition-colors"
                        >
                          {item.value}
                        </motion.button>
                      )}

                      {item.type === 'status' && (
                        <div className="flex items-center gap-2">
                          <motion.span
                            animate={{ opacity: [0.5, 1, 0.5] }}
                            transition={{ duration: 2, repeat: Infinity }}
                            className="w-1.5 h-1.5 rounded-full bg-emerald-400"
                          />
                          <span className="text-[10px] font-mono tracking-widest uppercase font-bold text-emerald-400 bg-emerald-500/10 px-2 py-1 border border-emerald-500/20 rounded">
                            {item.value}
                          </span>
                        </div>
                      )}
                    </motion.div>
                  ))}
                </div>
              </motion.div>
            );
          })}
        </motion.div>
      </div>
    </motion.div>
  );
}
