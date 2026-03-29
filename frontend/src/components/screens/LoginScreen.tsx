import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Shield, LogIn, ArrowLeft } from 'lucide-react';
import { motion } from 'motion/react';
import DarkVeil from '../ui/DarkVeil';
import BlurText from '../ui/BlurText';

interface LoginScreenProps {
  onLogin?: (email: string) => void;
  onBack?: () => void;
}

export default function LoginScreen({ onLogin, onBack }: LoginScreenProps) {
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      if (onLogin) onLogin(email);
      navigate('/app/dashboard');
    }, 1500);
  };

  const handleBack = () => {
    if (onBack) onBack();
    navigate('/');
  };

  return (
    <div className="relative min-h-screen flex flex-col items-center justify-center p-6 overflow-hidden">
      <DarkVeil />

      {/* Back Button */}
      <motion.button
        onClick={handleBack}
        initial={{ opacity: 0, x: -20 }}
        animate={{ opacity: 1, x: 0 }}
        transition={{ delay: 0.2 }}
        whileHover={{ x: -4 }}
        className="absolute top-8 left-8 text-gray-400 hover:text-white flex items-center gap-2 transition-colors z-20"
      >
        <ArrowLeft className="w-5 h-5" />
        <span className="font-medium text-sm">Return to Platform</span>
      </motion.button>

      {/* Main Content */}
      <motion.div
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="w-full max-w-md z-10 mt-12"
      >
        <div className="text-center mb-10 pb-6 border-b border-white/10 relative">
          <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2, type: 'spring', stiffness: 300 }}
            className="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-indigo-500/10 border border-indigo-500/30 mb-6 shadow-[0_0_30px_rgba(99,102,241,0.3)]"
          >
            <Shield className="w-8 h-8 text-indigo-400" />
          </motion.div>

          <BlurText
            text="Secure Access"
            className="text-4xl md:text-5xl font-bold font-heading text-white mb-4"
            animateBy="words"
            direction="top"
          />
          <motion.p
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="text-gray-400 font-mono text-sm tracking-widest uppercase mt-4"
          >
            Intelligence Engine Authentication
          </motion.p>
        </div>

        <motion.form
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.5 }}
          onSubmit={handleSubmit}
          className="bg-black/40 backdrop-blur-xl border border-white/10 p-8 rounded-3xl relative overflow-hidden shadow-2xl"
        >
          <div className="absolute top-0 left-0 w-full h-px bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent" />
          <div className="absolute inset-0 bg-gradient-to-b from-indigo-500/5 to-transparent pointer-events-none rounded-3xl" />

          <div className="space-y-6 relative z-10">
            <div className="space-y-2">
              <label className="text-[10px] font-bold uppercase tracking-[0.2em] text-indigo-400">
                Security Credentials
              </label>
              <motion.input
                whileFocus={{ borderColor: 'rgba(99,102,241,0.6)', boxShadow: '0 0 20px rgba(99,102,241,0.15)' }}
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="operator@auditpilot.ai"
                className="w-full bg-black/60 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all font-mono text-sm"
                required
              />
            </div>

            <div className="space-y-2">
              <div className="flex justify-between items-center">
                <label className="text-[10px] font-bold uppercase tracking-[0.2em] text-indigo-400">
                  Access Token
                </label>
                <a href="#" className="text-xs text-indigo-400 hover:text-indigo-300 transition-colors">
                  Reset Token?
                </a>
              </div>
              <motion.input
                whileFocus={{ borderColor: 'rgba(99,102,241,0.6)', boxShadow: '0 0 20px rgba(99,102,241,0.15)' }}
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••••••"
                className="w-full bg-black/60 border border-white/10 rounded-xl px-4 py-3 text-white placeholder:text-gray-600 focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/50 transition-all font-mono tracking-widest"
                required
              />
            </div>

            <motion.button
              type="submit"
              disabled={isLoading}
              whileHover={{ scale: 1.01, boxShadow: '0 0 30px rgba(99,102,241,0.5)' }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 disabled:opacity-60 text-white font-bold py-4 rounded-xl flex items-center justify-center gap-3 transition-all shadow-[0_0_20px_rgba(99,102,241,0.3)] mt-8 group relative overflow-hidden"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-transparent via-white/10 to-transparent -translate-x-[100%] group-hover:translate-x-[100%] transition-transform duration-700" />
              {isLoading ? (
                <>
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  <span className="font-mono text-xs uppercase tracking-widest">Verifying Signature...</span>
                </>
              ) : (
                <>
                  <span className="tracking-wide">Initialize Connection</span>
                  <LogIn className="w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </>
              )}
            </motion.button>
          </div>
        </motion.form>

        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 0.6 }}
          transition={{ delay: 0.6 }}
          className="mt-12 flex flex-col items-center gap-4 border-t border-white/10 pt-8 hover:opacity-100 transition-opacity"
        >
          <div className="flex gap-6 text-[10px] font-bold uppercase tracking-[0.3em] text-gray-400">
            <a href="#" className="hover:text-indigo-400 transition-colors">Privacy</a>
            <a href="#" className="hover:text-indigo-400 transition-colors">System Status</a>
            <a href="#" className="hover:text-indigo-400 transition-colors">Support</a>
          </div>
          <p className="text-[10px] text-gray-600 font-mono tracking-widest">v2.4.0-KINETIC NODE SECURE</p>
        </motion.div>
      </motion.div>
    </div>
  );
}
