import React, { useState, useEffect } from 'react';
import { Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { AnimatePresence, motion } from 'motion/react';
import { Sidebar, Topbar } from './Navigation';
import DashboardScreen from './DashboardScreen';
import VendorScreens from './VendorScreens';
import WorkflowsScreen from './WorkflowsScreen';
import AnalyticsScreen from './AnalyticsScreen';
import AuditsScreen from './AuditsScreen';
import SettingsScreen from './SettingsScreen';
import { X, User } from 'lucide-react';

const SCREEN_MAP: Record<string, React.ComponentType> = {
  dashboard: DashboardScreen,
  vendors: VendorScreens,
  workflows: WorkflowsScreen,
  audits: AuditsScreen,
  analytics: AnalyticsScreen,
  settings: SettingsScreen,
};

export default function AppView({ onLogout, userEmail = 'System Operator' }: { onLogout?: () => void, userEmail?: string }) {
  const navigate = useNavigate();
  const location = useLocation();
  const [isDemoMode, setIsDemoMode] = useState(false);

  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      if (e.ctrlKey && e.altKey && e.key.toLowerCase() === 'd') {
        e.preventDefault();
        setIsDemoMode(prev => !prev);
      }
    };
    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  // Derive current screen from URL
  const pathSegment = location.pathname.split('/').pop() || 'dashboard';
  const currentScreen = SCREEN_MAP[pathSegment] ? pathSegment : 'dashboard';

  const handleNavigate = (screen: string) => {
    navigate(`/app/${screen}`);
  };

  const handleLogout = () => {
    if (onLogout) onLogout();
    navigate('/');
  };

  return (
    <div className={`min-h-screen bg-[#020202] text-gray-100 font-sans antialiased overflow-hidden ${isDemoMode ? 'demo-active' : ''}`}>
      {/* Ambient Background */}
      <div className="fixed top-[-20%] right-[-10%] w-[800px] h-[800px] bg-indigo-500/10 blur-[150px] rounded-full -z-10 pointer-events-none" />
      <div className="fixed bottom-[-10%] left-[-10%] w-[600px] h-[600px] bg-violet-900/10 blur-[120px] rounded-full -z-10 pointer-events-none" />
      <div className="fixed top-[40%] left-[30%] w-[400px] h-[400px] bg-indigo-900/5 blur-[100px] rounded-full -z-10 pointer-events-none" />

      {!isDemoMode && (
        <Sidebar currentScreen={currentScreen} onNavigate={handleNavigate} onLogout={handleLogout} />
      )}

      <div className={`${isDemoMode ? 'ml-0' : 'ml-72'} flex flex-col min-h-screen relative z-10 transition-all duration-700 ease-in-out`}>
        {!isDemoMode && <Topbar userEmail={userEmail} />}

        <main className={`${isDemoMode ? 'pt-10 px-20' : 'pt-28 px-10'} pb-12 flex-1 max-h-screen overflow-y-auto custom-scrollbar transition-all duration-700`}>
          <AnimatePresence mode="wait" initial={false}>
            <Routes location={location} key={location.pathname}>
              <Route path="dashboard" element={<ScreenWrapper><DashboardScreen /></ScreenWrapper>} />
              <Route path="workflows" element={<ScreenWrapper><WorkflowsScreen /></ScreenWrapper>} />
              <Route path="audits" element={<ScreenWrapper><AuditsScreen /></ScreenWrapper>} />
              <Route path="vendors" element={<ScreenWrapper><VendorScreens /></ScreenWrapper>} />
              <Route path="analytics" element={<ScreenWrapper><AnalyticsScreen /></ScreenWrapper>} />
              <Route path="settings" element={<ScreenWrapper><SettingsScreen /></ScreenWrapper>} />
              <Route path="*" element={<Navigate to="/app/dashboard" replace />} />
            </Routes>
          </AnimatePresence>
        </main>
      </div>

      <GreetingPopup userEmail={userEmail} />
    </div>
  );
}

// ─── Screen wrapper with animation ───────────────────────────────────────────
function ScreenWrapper({ children }: { children: React.ReactNode }) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 24, filter: 'blur(8px)' }}
      animate={{ opacity: 1, y: 0, filter: 'blur(0px)' }}
      exit={{ opacity: 0, y: -16, filter: 'blur(4px)' }}
      transition={{ duration: 0.4, ease: [0.22, 1, 0.36, 1] }}
    >
      {children}
    </motion.div>
  );
}

// ─── Greeting Popup ───────────────────────────────────────────────────────────
const GreetingPopup = ({ userEmail = 'System Operator' }: { userEmail?: string }) => {
  const [isVisible, setIsVisible] = useState(true);

  const currentHour = new Date().getHours();
  let greeting = 'Good Evening';
  if (currentHour >= 5 && currentHour < 12) {
    greeting = 'Good Morning';
  } else if (currentHour >= 12 && currentHour < 17) {
    greeting = 'Good Afternoon';
  }

  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          initial={{ opacity: 0, y: 60, x: 40, scale: 0.9 }}
          animate={{ opacity: 1, y: 0, x: 0, scale: 1 }}
          exit={{ opacity: 0, y: 60, x: 40, scale: 0.9 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30, delay: 0.4 }}
          className="fixed bottom-8 right-8 z-50 bg-[#0a0a0a]/90 backdrop-blur-xl border border-white/10 p-4 rounded-2xl shadow-[0_0_40px_rgba(99,102,241,0.2)] flex items-center gap-4 min-w-[280px]"
        >
          {/* Glow border */}
          <div className="absolute inset-0 rounded-2xl bg-gradient-to-br from-indigo-500/10 to-transparent pointer-events-none" />
          <motion.div
            animate={{ scale: [1, 1.05, 1] }}
            transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
            className="h-10 w-10 rounded-full flex items-center justify-center border border-indigo-500/40 bg-indigo-500/10 shrink-0"
          >
            <User className="w-5 h-5 text-indigo-400" />
          </motion.div>
          <div className="flex-1 max-w-[200px] relative z-10">
            <h4 className="text-white font-bold text-sm">{greeting},</h4>
            <p className="text-indigo-400 font-mono text-[10px] uppercase tracking-wider truncate" title={userEmail}>
              {userEmail}
            </p>
          </div>
          <button
            onClick={() => setIsVisible(false)}
            className="text-gray-500 hover:text-white transition-colors bg-white/5 hover:bg-white/10 rounded-full p-1 relative z-10"
          >
            <X className="w-4 h-4" />
          </button>
        </motion.div>
      )}
    </AnimatePresence>
  );
};
