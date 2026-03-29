import { useState } from "react";
import { Shield, Twitter, Github, Linkedin, ArrowRight, CheckCircle2 } from "lucide-react";
import { cn } from "../../lib/utils";
import { useNavigate } from "react-router-dom";

export const Footer = () => {
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [subscribed, setSubscribed] = useState(false);

  const handleSubscribe = (e: React.FormEvent) => {
    e.preventDefault();
    if (email.trim() && email.includes('@')) {
      setSubscribed(true);
      setTimeout(() => setSubscribed(false), 5000);
      setEmail("");
    }
  };

  const handleNavigation = (item: string) => {
    const internalPaths: Record<string, string> = {
      'Features': '#features',
      'Pricing': '#pricing',
      'Use Cases': '#use-cases',
      'FAQ': '#faq'
    };

    if (item === 'Dashboard') {
      navigate('/login');
    } else if (internalPaths[item]) {
      window.location.hash = internalPaths[item];
    } else {
      // Dynamic missing page routes
      navigate('/' + item.toLowerCase().replace(/\s+/g, '-'));
    }
  };

  const socialLinks = [
    { icon: Twitter, url: 'https://twitter.com' },
    { icon: Github, url: 'https://github.com' },
    { icon: Linkedin, url: 'https://linkedin.com' }
  ];

  return (
    <footer className="relative bg-[#020202] text-white pt-24 pb-12 overflow-hidden border-t border-white/5">
      {/* Background glow effects */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 w-3/4 h-1/2 bg-indigo-500/10 blur-[120px] rounded-[100%] pointer-events-none" />
      <div className="absolute bottom-0 right-0 w-1/3 h-1/3 bg-indigo-500/10 blur-[100px] rounded-[100%] pointer-events-none" />

      <div className="max-w-7xl mx-auto px-6 relative z-10">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-12 lg:gap-8 mb-16">
          <div className="col-span-1 lg:col-span-2">
            <div className="flex items-center gap-3 mb-6 relative group inline-flex cursor-pointer" onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}>
              <div className="absolute -inset-2 bg-indigo-500/20 rounded-full blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
              <div className="w-10 h-10 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20 relative z-10">
                <Shield className="text-white w-5 h-5" />
              </div>
              <span
                className={cn(
                  "text-2xl font-bold tracking-tight font-heading relative z-10 inline-block hero-glow-text",
                  "before:absolute before:opacity-0 before:content-[attr(data-text)]",
                  "before:bg-[linear-gradient(0deg,#dfe5ee_0%,#fffaf6_50%)] before:bg-clip-text before:text-[#fffaf6]",
                )}
                style={{ filter: "url(#glow-4)" }}
                data-text="AuditPilot"
              >
                AuditPilot
              </span>
            </div>
            <p className="text-gray-400 leading-relaxed mb-8 max-w-sm">
              The modern standard for audit workflow and monitoring. Built for clarity, speed, and precision in the era of AI.
            </p>
            <div className="flex gap-5">
              {socialLinks.map((social, i) => {
                const Icon = social.icon;
                return (
                  <a key={i} href={social.url} target="_blank" rel="noopener noreferrer" className="w-10 h-10 rounded-full bg-white/5 flex items-center justify-center cursor-pointer hover:bg-white/10 hover:text-indigo-400 text-gray-400 transition-all hover:scale-110 border border-white/5 hover:border-indigo-500/30">
                    <Icon className="w-4 h-4" />
                  </a>
                );
              })}
            </div>
          </div>
          
          <div>
            <h4 className="text-white font-bold mb-6 font-heading tracking-wide">Product</h4>
            <ul className="space-y-4 text-gray-400 text-sm">
              {['Features', 'Dashboard', 'Integrations', 'Pricing', 'Changelog'].map(item => (
                <li key={item} onClick={() => handleNavigation(item)} className="hover:text-white cursor-pointer transition-colors flex items-center gap-2 group relative">
                  <ArrowRight className="w-3 h-3 opacity-0 -ml-5 group-hover:opacity-100 group-hover:ml-0 transition-all text-indigo-400" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-white font-bold mb-6 font-heading tracking-wide">Resources</h4>
            <ul className="space-y-4 text-gray-400 text-sm">
              {['Documentation', 'API Reference', 'Community', 'Support', 'Blog'].map(item => (
                <li key={item} onClick={() => handleNavigation(item)} className="hover:text-white cursor-pointer transition-colors flex items-center gap-2 group relative">
                  <ArrowRight className="w-3 h-3 opacity-0 -ml-5 group-hover:opacity-100 group-hover:ml-0 transition-all text-indigo-400" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <h4 className="text-white font-bold mb-6 font-heading tracking-wide">Company</h4>
            <ul className="space-y-4 text-gray-400 text-sm">
              {['About Us', 'Careers', 'Privacy Policy', 'Terms of Service', 'Contact'].map(item => (
                <li key={item} onClick={() => handleNavigation(item)} className="hover:text-white cursor-pointer transition-colors flex items-center gap-2 group relative">
                  <ArrowRight className="w-3 h-3 opacity-0 -ml-5 group-hover:opacity-100 group-hover:ml-0 transition-all text-indigo-400" />
                  <span>{item}</span>
                </li>
              ))}
            </ul>
          </div>
        </div>

        {/* Call to action Newsletter/Contact */}
        <div className="border border-white/10 bg-white/5 rounded-3xl p-8 md:p-12 mb-12 flex flex-col md:flex-row items-center justify-between gap-8 backdrop-blur-md relative overflow-hidden">
          <div className="absolute inset-0 bg-gradient-to-r from-indigo-500/10 to-indigo-500/10" />
          <div className="relative z-10 max-w-xl">
            <h3 className="text-2xl font-bold font-heading mb-2">Ready to secure your workflow?</h3>
            <p className="text-gray-400">Join over 5,000+ teams using AuditPilot to monitor and automate their audit operations beautifully.</p>
          </div>
          <form onSubmit={handleSubscribe} className="relative z-10 flex flex-col sm:flex-row w-full md:w-auto gap-3">
            <input 
              type="email" 
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email" 
              className="bg-black/50 border border-white/10 rounded-full px-6 py-3 text-sm text-white focus:outline-none focus:border-indigo-500 w-full sm:w-64 transition-colors disabled:opacity-50" 
              disabled={subscribed}
              required
            />
            <button 
              type="submit"
              disabled={subscribed}
              className={`font-semibold px-6 py-3 rounded-full text-sm transition-all whitespace-nowrap shadow-[0_0_20px_rgba(255,255,255,0.3)] hover:shadow-[0_0_30px_rgba(255,255,255,0.5)] flex items-center justify-center gap-2 ${
                subscribed 
                  ? 'bg-emerald-500 hover:bg-emerald-500 text-white shadow-[0_0_20px_rgba(16,185,129,0.3)]' 
                  : 'bg-white text-black hover:bg-indigo-50'
              }`}
            >
              {subscribed ? (
                <>
                  <CheckCircle2 className="w-4 h-4" />
                  Subscribed!
                </>
              ) : (
                'Subscribe'
              )}
            </button>
          </form>
        </div>

        <div className="flex flex-col md:flex-row justify-between items-center gap-4 text-sm text-gray-500 pt-8 border-t border-white/10">
          <div className="flex items-center gap-2">
            <div className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse" />
            <span>All systems operational</span>
          </div>
          <p>© {new Date().getFullYear()} AuditPilot Inc. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
};
