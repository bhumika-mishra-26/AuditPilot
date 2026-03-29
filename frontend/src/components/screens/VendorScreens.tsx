import React, { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'motion/react';
import { Store, UserCheck, AlertTriangle, ArrowUpRight, Loader2, Plus, X } from 'lucide-react';
import TiltedCard from '../ui/TiltedCard';
import { listVendors, onboardVendor, type Vendor } from '../../lib/api';
import { staggerContainer, itemVariants, cardVariants } from '../ui/PageTransition';

export default function VendorScreens() {
  const [vendors, setVendors] = useState<Vendor[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [newVendor, setNewVendor] = useState({ vendor_id: '', name: '' });
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const fetchVendors = async () => {
    try {
      setLoading(true);
      const data = await listVendors();
      setVendors(data);
    } catch (err) {
      console.error('Failed to fetch vendors:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { fetchVendors(); }, []);

  const handleOnboard = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newVendor.vendor_id || !newVendor.name) return;
    setIsSubmitting(true);
    setError(null);
    try {
      await onboardVendor(newVendor);
      setShowModal(false);
      setNewVendor({ vendor_id: '', name: '' });
      fetchVendors();
    } catch (err: any) {
      setError(err.message || 'Onboarding failed');
    } finally {
      setIsSubmitting(false);
    }
  };

  const getIcon = (risk: string) => {
    if (risk === 'Critical') return AlertTriangle;
    if (risk === 'Medium') return UserCheck;
    return Store;
  };

  const getColor = (risk: string) => {
    if (risk === 'Critical') return 'text-red-400';
    if (risk === 'Medium') return 'text-yellow-400';
    return 'text-emerald-400';
  };

  const getBg = (risk: string) => {
    if (risk === 'Critical') return 'bg-red-400/10 border-red-400/20';
    if (risk === 'Medium') return 'bg-yellow-400/10 border-yellow-400/20';
    return 'bg-emerald-400/10 border-emerald-400/20';
  };

  const getRiskGlow = (risk: string) => {
    if (risk === 'Critical') return '0 0 30px rgba(248,113,113,0.15)';
    if (risk === 'Medium') return '0 0 30px rgba(250,204,21,0.1)';
    return '0 0 30px rgba(52,211,153,0.1)';
  };

  return (
    <motion.div
      variants={staggerContainer}
      initial="initial"
      animate="animate"
      className="space-y-10"
    >
      {/* Header */}
      <motion.div variants={itemVariants} className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-black font-heading text-white tracking-tight uppercase">
            Vendor Intelligence
          </h1>
          <p className="text-gray-500 font-mono text-xs tracking-widest uppercase mt-2">
            Active Entities:{' '}
            <motion.span
              key={vendors.length}
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-indigo-400"
            >
              {vendors.length}
            </motion.span>
          </p>
        </div>
        <motion.button
          whileHover={{ scale: 1.03, boxShadow: '0 0 25px rgba(99,102,241,0.5)' }}
          whileTap={{ scale: 0.97 }}
          onClick={() => setShowModal(true)}
          className="bg-gradient-to-r from-indigo-600 to-violet-600 hover:from-indigo-500 hover:to-violet-500 text-white px-6 py-3 rounded-xl font-bold shadow-[0_0_20px_rgba(99,102,241,0.3)] transition-all flex items-center gap-3"
        >
          <motion.div whileHover={{ rotate: 90 }} transition={{ duration: 0.3 }}>
            <Plus className="w-5 h-5" />
          </motion.div>
          Onboard Vendor
        </motion.button>
      </motion.div>

      {loading ? (
        <div className="flex items-center justify-center py-24">
          <motion.div
            animate={{ rotate: 360 }}
            transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
          >
            <Loader2 className="w-10 h-10 text-indigo-400" />
          </motion.div>
        </div>
      ) : (
        <motion.div
          variants={staggerContainer}
          className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6"
        >
          {vendors.map((vendor, i) => {
            const Icon = getIcon(vendor.risk);
            const color = getColor(vendor.risk);
            const bg = getBg(vendor.risk);
            return (
              <motion.div
                key={i}
                variants={cardVariants}
                whileHover={{
                  y: -8,
                  scale: 1.02,
                  boxShadow: getRiskGlow(vendor.risk),
                }}
                transition={{ type: 'spring', stiffness: 300, damping: 20 }}
              >
                <TiltedCard className="bg-black/40 border-white/10 hover:bg-black/60">
                  <div className="flex justify-between items-start mb-6">
                    <motion.div
                      whileHover={{ scale: 1.15, rotate: 10 }}
                      className={`w-12 h-12 rounded-xl flex items-center justify-center border ${bg} ${color}`}
                    >
                      <Icon className="w-6 h-6" />
                    </motion.div>
                    <div className="text-[10px] font-mono text-gray-600">{vendor.vendor_id}</div>
                  </div>

                  <h3 className="text-xl font-bold text-white mb-2 truncate" title={vendor.name}>
                    {vendor.name}
                  </h3>

                  <div className="space-y-3 font-mono text-xs uppercase tracking-wide mt-6">
                    <div className="flex justify-between">
                      <span className="text-gray-500">Status</span>
                      <span className={color}>{vendor.status}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">Risk Profile</span>
                      <span className={color}>{vendor.risk}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-gray-500">YTD Spend</span>
                      <span className="text-white font-bold tracking-tight">{vendor.spend}</span>
                    </div>
                  </div>

                  <div className="mt-8 pt-4 border-t border-white/10">
                    <motion.button
                      whileHover={{ color: '#fff', x: 4 }}
                      className="w-full py-2 text-center text-xs font-bold text-indigo-400 hover:bg-indigo-500/10 rounded-lg transition-colors flex items-center justify-center gap-1"
                    >
                      View Ledger <ArrowUpRight className="w-3 h-3" />
                    </motion.button>
                  </div>
                </TiltedCard>
              </motion.div>
            );
          })}
        </motion.div>
      )}

      {/* Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-[100] flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm"
          >
            <motion.div
              initial={{ scale: 0.9, opacity: 0, y: 20 }}
              animate={{ scale: 1, opacity: 1, y: 0 }}
              exit={{ scale: 0.9, opacity: 0, y: 20 }}
              transition={{ type: 'spring', stiffness: 300, damping: 30 }}
              className="bg-[#0a0a0a] border border-white/10 p-8 rounded-2xl w-full max-w-md shadow-[0_0_60px_rgba(99,102,241,0.2)] relative overflow-hidden"
            >
              <div className="absolute top-0 left-0 right-0 h-px bg-gradient-to-r from-transparent via-indigo-500/50 to-transparent" />
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-bold text-white uppercase tracking-tight">Onboard New Entity</h2>
                <motion.button
                  whileHover={{ scale: 1.1, rotate: 90 }}
                  onClick={() => setShowModal(false)}
                  className="text-gray-500 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </motion.button>
              </div>

              <form onSubmit={handleOnboard} className="space-y-6">
                <div>
                  <label className="block text-[10px] font-mono text-indigo-400 uppercase tracking-widest mb-2">
                    Vendor ID
                  </label>
                  <input
                    type="text"
                    value={newVendor.vendor_id}
                    onChange={(e) => setNewVendor({ ...newVendor, vendor_id: e.target.value })}
                    placeholder="e.g. V-001"
                    className="w-full bg-black border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/30 transition-all"
                    required
                  />
                </div>
                <div>
                  <label className="block text-[10px] font-mono text-indigo-400 uppercase tracking-widest mb-2">
                    Legal Name
                  </label>
                  <input
                    type="text"
                    value={newVendor.name}
                    onChange={(e) => setNewVendor({ ...newVendor, name: e.target.value })}
                    placeholder="e.g. Acme Corp"
                    className="w-full bg-black border border-white/10 rounded-xl px-4 py-3 text-sm text-white focus:outline-none focus:border-indigo-500/50 focus:ring-1 focus:ring-indigo-500/30 transition-all"
                    required
                  />
                </div>
                {error && <p className="text-red-400 text-[10px] font-mono">{error}</p>}
                <motion.button
                  type="submit"
                  disabled={isSubmitting}
                  whileHover={{ scale: 1.01, boxShadow: '0 0 25px rgba(99,102,241,0.4)' }}
                  whileTap={{ scale: 0.98 }}
                  className="w-full bg-gradient-to-r from-indigo-600 to-violet-600 disabled:opacity-50 text-white font-bold py-4 rounded-xl shadow-lg flex items-center justify-center gap-2"
                >
                  {isSubmitting ? <Loader2 className="w-5 h-5 animate-spin" /> : <Store className="w-5 h-5" />}
                  CONFIRM ONBOARDING
                </motion.button>
              </form>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}
