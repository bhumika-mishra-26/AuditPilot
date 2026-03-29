import React from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion, AnimatePresence } from 'motion/react';
import {
  LayoutDashboard,
  GitBranch,
  ClipboardCheck,
  Store,
  Activity,
  Settings,
  Plus,
  CircleHelp,
  LogOut,
  Search,
  Bell,
  Network,
  User,
  Zap,
} from 'lucide-react';

const navItems = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'workflows', label: 'Workflows', icon: GitBranch },
  { id: 'audits', label: 'Audits', icon: ClipboardCheck },
  { id: 'vendors', label: 'Vendors', icon: Store },
  { id: 'analytics', label: 'Analytics', icon: Activity },
  { id: 'settings', label: 'Settings', icon: Settings },
];

interface SidebarProps {
  currentScreen: string;
  onNavigate: (screen: string) => void;
  onLogout: () => void;
}

export const Sidebar = ({ currentScreen, onNavigate, onLogout }: SidebarProps) => {
  const navigate = useNavigate();
  const location = useLocation();

  const isActive = (id: string) => {
    return location.pathname === `/app/${id}` || (id === 'dashboard' && location.pathname === '/app');
  };

  return (
    <aside className="h-screen w-72 flex flex-col fixed left-0 top-0 border-r border-white/[0.06] bg-black/50 backdrop-blur-2xl shadow-[1px_0_0_rgba(255,255,255,0.04)] z-50">
      {/* Top glow */}
      <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-indigo-500/40 to-transparent" />

      {/* Logo */}
      <motion.div
        initial={{ opacity: 0, y: -10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
        className="p-8 pb-6"
      >
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center shadow-[0_0_20px_rgba(99,102,241,0.3)]">
            <Zap className="w-4 h-4 text-indigo-400" />
          </div>
          <div>
            <h1 className="text-lg font-black tracking-tighter text-white uppercase font-heading leading-none">
              AuditPilot
            </h1>
            <p className="text-[9px] text-indigo-400 uppercase tracking-[0.2em] font-bold font-mono">
              Operations Portal
            </p>
          </div>
        </div>
      </motion.div>

      {/* Nav */}
      <nav className="flex-1 px-4 space-y-1 mt-2">
        {navItems.map((item, idx) => {
          const Icon = item.icon;
          const active = isActive(item.id);
          return (
            <motion.div
              key={item.id}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: idx * 0.06, duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
              className="relative"
            >
              {active && (
                <motion.div
                  layoutId="active-nav-bg"
                  className="absolute inset-0 rounded-xl bg-indigo-500/10 border border-indigo-500/20"
                  transition={{ type: 'spring', stiffness: 400, damping: 35 }}
                />
              )}
              {active && (
                <motion.div
                  layoutId="active-nav-bar"
                  className="absolute left-0 top-1/2 -translate-y-1/2 w-0.5 h-5 bg-indigo-400 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.8)]"
                  transition={{ type: 'spring', stiffness: 400, damping: 35 }}
                />
              )}
              <motion.button
                onClick={() => navigate(`/app/${item.id}`)}
                whileHover={{ x: active ? 0 : 4 }}
                whileTap={{ scale: 0.97 }}
                transition={{ duration: 0.2 }}
                className={`relative w-full flex items-center gap-3 px-4 py-3 rounded-xl group z-10 ${
                  active
                    ? 'text-indigo-300'
                    : 'text-gray-500 hover:text-gray-200'
                }`}
              >
                <motion.div
                  whileHover={{ scale: 1.1, rotate: active ? 0 : 5 }}
                  transition={{ duration: 0.2 }}
                >
                  <Icon className={`w-4.5 h-4.5 ${active ? 'text-indigo-400' : ''}`} style={{ width: '18px', height: '18px' }} />
                </motion.div>
                <span className={`font-semibold text-sm tracking-wide ${active ? 'text-white' : ''}`}>
                  {item.label}
                </span>
                {active && (
                  <motion.span
                    initial={{ opacity: 0, scale: 0 }}
                    animate={{ opacity: 1, scale: 1 }}
                    className="ml-auto w-1.5 h-1.5 rounded-full bg-indigo-400 shadow-[0_0_6px_rgba(99,102,241,0.8)]"
                  />
                )}
              </motion.button>
            </motion.div>
          );
        })}
      </nav>

      {/* Deploy CTA */}
      <div className="px-5 mb-4">
        <motion.button
          whileHover={{ scale: 1.02, boxShadow: '0 0 30px rgba(99,102,241,0.5)' }}
          whileTap={{ scale: 0.98 }}
          className="w-full py-3.5 bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white rounded-xl font-bold shadow-[0_0_20px_rgba(99,102,241,0.3)] transition-all flex items-center justify-center gap-2 group text-sm"
        >
          <motion.div
            whileHover={{ rotate: 90 }}
            transition={{ duration: 0.3 }}
          >
            <Plus className="w-4 h-4" />
          </motion.div>
          Deploy Agent
        </motion.button>
      </div>

      {/* Bottom */}
      <div className="p-4 border-t border-white/[0.06] space-y-1">
        <motion.button
          whileHover={{ x: 4, color: '#fff' }}
          className="w-full flex items-center gap-3 px-4 py-2.5 text-gray-500 hover:text-white hover:bg-white/5 transition-colors rounded-lg"
        >
          <CircleHelp className="w-4 h-4" />
          <span className="font-semibold text-sm">Protocol Help</span>
        </motion.button>
        <motion.button
          onClick={onLogout}
          whileHover={{ x: 4 }}
          className="w-full flex items-center gap-3 px-4 py-2.5 text-gray-500 hover:text-red-400 hover:bg-red-500/10 transition-all rounded-lg group"
        >
          <LogOut className="w-4 h-4 group-hover:translate-x-0.5 transition-transform" />
          <span className="font-semibold text-sm">Terminate Session</span>
        </motion.button>
      </div>

      {/* Bottom glow */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />
    </aside>
  );
};

export const Topbar = ({ userEmail = 'System Operator' }: { userEmail?: string }) => {
  const [isConnected, setIsConnected] = React.useState(true);

  React.useEffect(() => {
    let mounted = true;
    const checkHealth = async () => {
      try {
        const res = await fetch("http://localhost:8000/api/v1/health", { signal: AbortSignal.timeout(3000) });
        if (mounted) setIsConnected(res.ok);
      } catch {
        if (mounted) setIsConnected(false);
      }
    };
    checkHealth();
    const interval = setInterval(checkHealth, 5000);
    return () => {
      mounted = false;
      clearInterval(interval);
    };
  }, []);

  const activePlan = localStorage.getItem('auditpilot_plan') || 'free';
  const planDisplay = activePlan === 'enterprise' ? 'Enterprise' : activePlan === 'pro' ? 'Pro ⭐' : 'Free';

  return (
    <motion.header
      initial={{ opacity: 0, y: -20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
      className="fixed top-0 right-0 h-20 bg-black/40 backdrop-blur-xl flex justify-between items-center w-[calc(100%-18rem)] px-8 z-40 border-b border-white/[0.06] shadow-sm"
    >
      {/* Bottom border line */}
      <div className="absolute bottom-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-white/10 to-transparent" />

      <div className="flex items-center gap-6 w-1/2">
        {/* Search */}
        <div className="relative w-full max-w-md group">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500 w-4 h-4 group-focus-within:text-indigo-400 transition-colors" />
          <input
            className="w-full bg-white/[0.04] text-white border border-white/[0.08] rounded-full py-2.5 pl-12 pr-4 text-sm focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/30 focus:bg-white/[0.06] placeholder:text-gray-600 transition-all font-mono"
            placeholder="Search nodes, reports, vendors..."
            type="text"
          />
        </div>
        <div className="h-4 w-px bg-white/10" />
        <div className="flex items-center gap-2 shrink-0">
          <motion.span
            animate={isConnected ? { opacity: [0.6, 1, 0.6] } : { opacity: [0.8, 0.4, 0.8] }}
            transition={{ duration: 2, repeat: Infinity }}
            className={`w-2 h-2 rounded-full ${isConnected ? 'bg-emerald-400 shadow-[0_0_10px_rgba(52,211,153,0.6)]' : 'bg-red-500 shadow-[0_0_10px_rgba(239,68,68,0.6)]'}`}
          />
          <span className={`font-mono font-bold text-[9px] tracking-[0.2em] uppercase whitespace-nowrap ${isConnected ? 'text-emerald-400' : 'text-red-500'}`}>
            {isConnected ? 'System Optimal' : 'System Offline'}
          </span>
        </div>
      </div>

      <div className="flex items-center gap-3">
        <motion.button
          whileHover={{ scale: 1.1 }}
          whileTap={{ scale: 0.95 }}
          className="p-2 text-gray-500 hover:text-white transition-colors relative"
        >
          <Bell className="w-5 h-5" />
          <motion.span
            animate={{ scale: [1, 1.3, 1] }}
            transition={{ duration: 2, repeat: Infinity }}
            className="absolute top-2 right-2 w-1.5 h-1.5 bg-indigo-500 rounded-full shadow-[0_0_8px_rgba(99,102,241,0.8)]"
          />
        </motion.button>
        <motion.button
          whileHover={{ scale: 1.1, rotate: 15 }}
          whileTap={{ scale: 0.95 }}
          className="p-2 text-gray-500 hover:text-white transition-colors"
        >
          <Network className="w-5 h-5" />
        </motion.button>

        <div className="flex items-center gap-3 pl-3 border-l border-white/10 group cursor-pointer ml-1">
          <div className="text-right">
            <p className="text-xs font-bold text-white truncate max-w-[150px]" title={userEmail}>
              {userEmail}
            </p>
            <p className={`text-[9px] font-mono tracking-wider font-bold uppercase ${activePlan === 'pro' ? 'text-amber-400' : 'text-indigo-400'}`}>
              Plan: {planDisplay}
            </p>
          </div>
          <motion.div
            whileHover={{ scale: 1.05, borderColor: 'rgba(99,102,241,0.6)' }}
            className="h-9 w-9 rounded-full bg-indigo-900/40 flex items-center justify-center border border-white/20 shadow-[0_0_15px_rgba(99,102,241,0.15)] transition-all"
          >
            <User className="w-4 h-4 text-indigo-400" />
          </motion.div>
        </div>
      </div>
    </motion.header>
  );
};
