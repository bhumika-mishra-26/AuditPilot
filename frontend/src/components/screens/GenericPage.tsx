import React, { useEffect } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { motion } from 'motion/react';
import { ArrowLeft, Clock, Construction, LayoutTemplate } from 'lucide-react';
import { Navbar } from '../layout/Navbar';
import { Footer } from '../layout/Footer';
export default function GenericPage() {
  const location = useLocation();
  const navigate = useNavigate();

  // Parse path to title (e.g. /api-reference -> API Reference)
  const rawPath = location.pathname.split('/').pop() || 'Page';
  const title = rawPath
    .split('-')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');

  // Scroll to top on mount
  useEffect(() => {
    window.scrollTo(0, 0);
  }, [location.pathname]);

  return (
    <div className="min-h-screen font-sans text-gray-100 flex flex-col relative overflow-hidden">
      <Navbar
        onLoginClick={() => navigate("/login")}
        onDashboardClick={() => navigate("/login")}
      />

      <main className="flex-1 flex flex-col pt-40 pb-20 relative z-10 px-6 max-w-5xl mx-auto w-full">
        <motion.button
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          onClick={() => navigate(-1)}
          className="flex items-center gap-2 text-indigo-400 hover:text-indigo-300 font-mono text-xs uppercase tracking-wider mb-16 transition-colors w-fit group"
        >
          <ArrowLeft className="w-4 h-4 group-hover:-translate-x-1 transition-transform" />
          Go Back
        </motion.button>
        
        <div className="flex flex-col items-center justify-center text-center max-w-3xl mx-auto mt-20">
          <motion.div
            initial={{ opacity: 0, scale: 0.8, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            className="w-20 h-20 rounded-2xl bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-center shadow-[0_0_50px_rgba(99,102,241,0.2)] mb-8"
          >
            <Construction className="w-10 h-10 text-indigo-400" />
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="text-5xl md:text-7xl font-bold font-heading tracking-tight mb-6"
          >
            {title}
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="text-xl text-gray-400 mb-12 font-medium"
          >
            This module represents the future home of the <span className="text-white font-bold">{title}</span> section. 
            Currently pending enterprise implementation in a future deployment cycle.
          </motion.p>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="inline-flex items-center gap-2 text-xs font-mono px-4 py-2 rounded-lg bg-white/5 border border-white/10 text-gray-500 uppercase tracking-widest"
          >
            <Clock className="w-3.5 h-3.5" />
            Under Construction
          </motion.div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
