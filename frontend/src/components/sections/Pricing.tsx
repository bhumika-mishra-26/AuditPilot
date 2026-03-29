import React, { useState } from 'react';
import { motion } from 'motion/react';
import { Check, X, Shield, Star, Rocket, ChevronRight } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

const pricingPlans = [
  {
    id: 'free',
    name: 'Free',
    target: 'Demo & Protfolio',
    price: { monthly: 0, yearly: 0 },
    description: 'Perfect for trying out generic systemic interactions.',
    features: [
      { name: 'W1 Onboarding Workflow', included: true },
      { name: '5 Workflows/day', included: true },
      { name: 'Limited Agents', included: true },
      { name: 'Morning Email Briefing', included: false },
      { name: 'Systemic Alerts', included: false },
      { name: 'W2/W3 Meeting AI', included: false },
      { name: 'Pattern Memory', included: false },
    ],
    cta: 'Start Free',
    popular: false,
  },
  {
    id: 'pro',
    name: 'Pro',
    target: 'Small Teams',
    price: { monthly: 1499, yearly: 1199 },
    description: 'Unlock full multi-agent orchestration and advanced workflows.',
    features: [
      { name: 'W1–W4 Full Workflows', included: true },
      { name: '300 Workflows/month', included: true },
      { name: 'Morning Email Briefing', included: true },
      { name: 'Advanced Pattern Memory', included: true },
      { name: 'Priority API Processing', included: true },
      { name: 'Systemic Alerts', included: true },
      { name: '10,000 AI tokens/month', included: true },
    ],
    cta: 'Upgrade to Pro',
    popular: true,
  },
  {
    id: 'enterprise',
    name: 'Enterprise',
    target: 'Scaling Companies',
    price: { monthly: 'Custom', yearly: 'Custom' },
    description: 'Bespoke integration and unlimited usage for enterprise scale.',
    features: [
      { name: 'Unlimited Workflows', included: true },
      { name: 'Multi-agent Collaboration', included: true },
      { name: 'Direct API Access', included: true },
      { name: 'Custom Integrations', included: true },
      { name: 'SLA + Dedicated Support', included: true },
      { name: 'Enterprise Pattern Memory', included: true },
      { name: 'On-Premises Deployment', included: true },
    ],
    cta: 'Book Demo',
    popular: false,
  }
];

export const Pricing = () => {
  const [isYearly, setIsYearly] = useState(false);
  const navigate = useNavigate();

  const handleSelectPlan = (planId: string) => {
    if (planId === 'enterprise') {
      window.location.href = "mailto:sales@auditpilot.ai";
      return;
    }
    // Save to local storage representing DB backend
    localStorage.setItem('auditpilot_plan', planId);
    // Shortcut straight to dashboard logic
    navigate('/app');
  };

  return (
    <section id="pricing" className="py-24 relative overflow-hidden bg-[#020202]">
      {/* Background Ambience */}
      <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-4xl h-[400px] bg-indigo-500/10 blur-[120px] rounded-full pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <div className="text-center mb-16 max-w-2xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-indigo-500/10 border border-indigo-500/20 text-indigo-400 text-xs font-mono font-bold uppercase tracking-wider mb-6"
          >
            <Shield className="w-3.5 h-3.5" />
            Designed for Scale
          </motion.div>
          <motion.h2
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.1 }}
            className="text-4xl md:text-5xl font-bold text-white font-heading tracking-tight mb-6"
          >
            Enterprise Workflows. 
            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-indigo-400 to-violet-400">
              Usage-Based Transparency.
            </span>
          </motion.h2>
          <motion.p
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="text-gray-400 text-lg mb-10"
          >
            SaaS pricing adapted for true multi-agent LLM systems. Standard workflows included. Predictable overages.
          </motion.p>

          {/* Pricing Toggle */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.3 }}
            className="flex items-center justify-center gap-4"
          >
            <span className={`text-sm font-semibold transition-colors ${!isYearly ? 'text-white' : 'text-gray-500'}`}>Monthly</span>
            <button
              onClick={() => setIsYearly(!isYearly)}
              className="relative w-16 h-8 rounded-full bg-white/5 border border-white/10 p-1 flex items-center transition-colors hover:bg-white/10 focus:outline-none focus:ring-2 focus:ring-indigo-500/50"
            >
              <motion.div
                animate={{ x: isYearly ? 32 : 0 }}
                transition={{ type: 'spring', stiffness: 500, damping: 30 }}
                className="w-6 h-6 rounded-full bg-indigo-500 shadow-[0_0_10px_rgba(99,102,241,0.5)]"
              />
            </button>
            <div className="flex items-center gap-2">
              <span className={`text-sm font-semibold transition-colors ${isYearly ? 'text-white' : 'text-gray-500'}`}>Annually</span>
              <span className="text-[10px] font-bold uppercase tracking-wider py-1 px-2 rounded-md bg-emerald-500/20 text-emerald-400 border border-emerald-500/20">
                Save 20%
              </span>
            </div>
          </motion.div>
        </div>

        {/* Pricing Cards */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 items-start">
          {pricingPlans.map((plan, index) => (
            <motion.div
              key={plan.id}
              initial={{ opacity: 0, y: 40 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.15, duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
              className={`relative rounded-3xl p-8 bg-black/40 backdrop-blur-xl border ${
                plan.popular 
                  ? 'border-indigo-500 shadow-[0_0_40px_rgba(99,102,241,0.15)]' 
                  : 'border-white/[0.08] hover:border-white/[0.15]'
              } transition-colors flex flex-col h-full group`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-3 py-1 bg-indigo-500 text-white text-[10px] font-bold uppercase tracking-widest rounded-full shadow-[0_0_15px_rgba(99,102,241,0.6)] flex items-center gap-1.5 whitespace-nowrap">
                  <Star className="w-3 h-3 fill-current" />
                  Most Popular
                </div>
              )}

              <div className="mb-6">
                <h3 className="text-xl font-bold text-white mb-1">{plan.name}</h3>
                <p className="text-xs text-gray-500 font-mono tracking-wider">{plan.target}</p>
              </div>

              <div className="mb-6 flex items-baseline gap-2">
                <span className="text-4xl font-black text-white font-heading">
                  {typeof plan.price.monthly === 'number' 
                    ? `₹${isYearly ? plan.price.yearly : plan.price.monthly}` 
                    : plan.price.monthly}
                </span>
                {typeof plan.price.monthly === 'number' && (
                  <span className="text-sm font-medium text-gray-500">/mo</span>
                )}
              </div>

              <p className="text-sm text-gray-400 mb-8 min-h-[40px] leading-relaxed">
                {plan.description}
              </p>

              <button
                onClick={() => handleSelectPlan(plan.id)}
                className={`w-full py-3.5 px-4 rounded-xl font-bold flex items-center justify-center gap-2 transition-all mb-8 shadow-sm ${
                  plan.popular
                    ? 'bg-indigo-600 hover:bg-indigo-500 text-white hover:shadow-[0_0_20px_rgba(99,102,241,0.4)]'
                    : 'bg-white/5 hover:bg-white/10 text-white border border-white/10'
                }`}
              >
                {plan.cta}
                <ChevronRight className={`w-4 h-4 ${plan.popular ? 'group-hover:translate-x-1 transition-transform' : ''}`} />
              </button>

              <div className="flex-1">
                <p className="text-xs font-bold text-white uppercase tracking-wider mb-4">Features Included</p>
                <ul className="space-y-3">
                  {plan.features.map((feature, i) => (
                    <li key={i} className={`flex items-start gap-3 text-sm ${feature.included ? 'text-gray-300' : 'text-gray-600'}`}>
                      {feature.included ? (
                        <div className="mt-0.5 w-4 h-4 rounded-full bg-emerald-500/20 flex items-center justify-center shrink-0">
                          <Check className="w-2.5 h-2.5 text-emerald-400" />
                        </div>
                      ) : (
                        <div className="mt-0.5 w-4 h-4 rounded-full bg-white/5 flex items-center justify-center shrink-0">
                          <X className="w-2.5 h-2.5 text-gray-500" />
                        </div>
                      )}
                      <span>{feature.name}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </motion.div>
          ))}
        </div>

        {/* Usage Based Transparency Add-on */}
        <motion.div 
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mt-16 bg-black/50 backdrop-blur-xl border border-white/10 rounded-2xl p-6 md:p-8 flex flex-col md:flex-row items-center justify-between gap-6"
        >
          <div className="flex items-center gap-4">
            <div className="w-12 h-12 rounded-xl bg-indigo-500/20 border border-indigo-500/30 flex items-center justify-center shrink-0">
              <Rocket className="w-6 h-6 text-indigo-400" />
            </div>
            <div>
              <h4 className="text-white font-bold mb-1">Scale as you Audit</h4>
              <p className="text-sm text-gray-400">Fair, transparent usage pricing past your monthly limits.</p>
            </div>
          </div>
          <div className="flex flex-wrap items-center gap-6">
            <div className="text-center md:text-left">
              <span className="block text-2xl font-black text-indigo-300">₹0.5</span>
              <span className="text-xs text-gray-500 font-mono tracking-widest uppercase">Per LLM Call</span>
            </div>
            <div className="w-px h-8 bg-white/10 hidden md:block"></div>
            <div className="text-center md:text-left">
              <span className="block text-2xl font-black text-violet-300">₹2.0</span>
              <span className="text-xs text-gray-500 font-mono tracking-widest uppercase">Per Extra Workflow</span>
            </div>
          </div>
        </motion.div>

      </div>
    </section>
  );
};
