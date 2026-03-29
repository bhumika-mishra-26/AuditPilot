import { Shield, Menu, X } from "lucide-react";
import { useState, useEffect } from "react";
import { cn } from "../../lib/utils";
import { motion, AnimatePresence } from "motion/react";

interface NavbarProps {
  onLoginClick: () => void;
  onDashboardClick: () => void;
}

export const Navbar = ({ onLoginClick, onDashboardClick }: NavbarProps) => {
  const [isScrolled, setIsScrolled] = useState(false);
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setIsScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll);
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <nav
      className={cn(
        "fixed top-6 left-1/2 -translate-x-1/2 z-50 transition-all duration-500",
        "w-[calc(100%-3rem)] max-w-6xl rounded-full",
        isScrolled ? "py-3 min-h-[70px]" : "py-4 min-h-[80px]"
      )}
      style={{
        // Ultra-transparent: just enough to read as glass, not as a panel
        background: "rgba(255, 255, 255, 0.05)",
        backdropFilter: "blur(12px) saturate(150%)",
        WebkitBackdropFilter: "blur(12px) saturate(150%)",
        // Single crisp border — the main thing that reads as "glass edge"
        border: "1px solid rgba(255, 255, 255, 0.15)",
        // Top inner highlight only — like light hitting the curved top of the glass
        boxShadow: `
          rgba(255, 255, 255, 0.2) -16px 0px 17px 8px, rgba(255, 255, 255, 0.04) 16px 0px 19px 20px, rgba(0, 0, 0, 0.15) 1px 1px 0px 0px
        `,
      }}
    >
      <div className="px-6 md:px-8 flex items-center justify-between relative z-10 w-full h-full">
        {/* Logo */}
        <div
          className="flex items-center gap-3 cursor-pointer group"
          onClick={() => window.scrollTo({ top: 0, behavior: "smooth" })}
        >
          <div className="relative">
            <div className="absolute -inset-2 bg-indigo-500/20 rounded-full blur-md opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
            <div className="w-9 h-9 bg-gradient-to-br from-indigo-500 to-indigo-600 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/20 relative z-10 transition-transform group-hover:scale-105">
              <Shield className="text-white w-5 h-5" />
            </div>
          </div>
          <span
            className={cn(
              "text-xl font-bold tracking-tight font-heading relative inline-block hero-glow-text",
              "before:absolute before:opacity-0 before:content-[attr(data-text)]",
              "before:bg-[linear-gradient(0deg,#dfe5ee_0%,#fffaf6_50%)] before:bg-clip-text before:text-[#fffaf6]"
            )}
            style={{ filter: "url(#glow-4)" }}
            data-text="AuditPilot"
          >
            AuditPilot
          </span>
        </div>

        {/* Desktop nav */}
        <div className="hidden md:flex items-center gap-1">
          {["Home", "Features", "Use Cases", "Pricing", "Dashboard", "FAQ"].map((item) =>
            item === "Dashboard" ? (
              <button
                key={item}
                onClick={onDashboardClick}
                className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white rounded-full transition-all cursor-pointer font-sans"
                style={{ background: "transparent", border: "none" }}
                onMouseEnter={(e) => {
                  const el = e.currentTarget as HTMLButtonElement;
                  el.style.background = "rgba(255,255,255,0.07)";
                  el.style.boxShadow = "inset 0 1px 0 rgba(255,255,255,0.1)";
                }}
                onMouseLeave={(e) => {
                  const el = e.currentTarget as HTMLButtonElement;
                  el.style.background = "transparent";
                  el.style.boxShadow = "none";
                }}
              >
                {item}
              </button>
            ) : (
              <a
                key={item}
                href={`#${item.toLowerCase().replace(" ", "-")}`}
                className="px-4 py-2 text-sm font-medium text-gray-300 hover:text-white rounded-full transition-all"
                style={{ background: "transparent" }}
                onMouseEnter={(e) => {
                  const el = e.currentTarget as HTMLAnchorElement;
                  el.style.background = "rgba(255,255,255,0.07)";
                  el.style.boxShadow = "inset 0 1px 0 rgba(255,255,255,0.1)";
                }}
                onMouseLeave={(e) => {
                  const el = e.currentTarget as HTMLAnchorElement;
                  el.style.background = "transparent";
                  el.style.boxShadow = "none";
                }}
              >
                {item}
              </a>
            )
          )}
        </div>

        {/* Sign In — glass button, NOT solid white */}
        <div className="hidden md:block">
          <button
            onClick={onLoginClick}
            style={{
              position: "relative",
              overflow: "hidden",
              background: "rgba(255, 255, 255, 0.01)",
              backdropFilter: "blur(8px)",
              WebkitBackdropFilter: "blur(8px)",
              color: "white",
              padding: "0.45rem 1.4rem",
              borderRadius: "9999px",
              fontSize: "0.875rem",
              fontWeight: 600,
              border: "1px solid rgba(255,255,255,0.25)",
              boxShadow: "inset 0 1px 0 rgba(255,255,255,0.2), 0 2px 8px rgba(0,0,0,0.2)",
              cursor: "pointer",
              transition: "all 0.2s ease",
            }}
            onMouseEnter={(e) => {
              const btn = e.currentTarget as HTMLButtonElement;
              btn.style.background = "rgba(255,255,255,0.14)";
              btn.style.borderColor = "rgba(255,255,255,0.4)";
              btn.style.boxShadow = "inset 0 1px 0 rgba(255,255,255,0.3), 0 4px 16px rgba(0,0,0,0.25)";
            }}
            onMouseLeave={(e) => {
              const btn = e.currentTarget as HTMLButtonElement;
              btn.style.background = "rgba(255,255,255,0.08)";
              btn.style.borderColor = "rgba(255,255,255,0.25)";
              btn.style.boxShadow = "inset 0 1px 0 rgba(255,255,255,0.2), 0 2px 8px rgba(0,0,0,0.2)";
            }}
          >
            Sign In
          </button>
        </div>

        {/* Mobile hamburger */}
        <button
          className="md:hidden text-white p-2 rounded-lg hover:bg-white/10 transition-colors"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
        >
          {mobileMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
        </button>
      </div>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileMenuOpen && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: -20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: -20 }}
            transition={{ type: "spring", bounce: 0, duration: 0.3 }}
            style={{
              position: "absolute",
              top: "calc(100% + 1rem)",
              left: 0,
              right: 0,
              background: "rgba(10, 10, 10, 0.25)",
              backdropFilter: "blur(20px) saturate(150%)",
              WebkitBackdropFilter: "blur(20px) saturate(150%)",
              border: "1px solid rgba(255,255,255,0.12)",
              borderRadius: "1.5rem",
              padding: "1.5rem",
              display: "flex",
              flexDirection: "column",
              gap: "0.25rem",
              boxShadow: "inset 0 1px 0 rgba(255,255,255,0.15), 0 20px 40px rgba(0,0,0,0.3)",
            }}
            className="md:hidden"
          >
            {["Home", "Features", "Use Cases", "Pricing", "Dashboard", "FAQ"].map((item) =>
              item === "Dashboard" ? (
                <button
                  key={item}
                  onClick={() => { setMobileMenuOpen(false); onDashboardClick(); }}
                  className="w-full text-left px-4 py-3 text-sm font-medium text-gray-300 hover:text-white rounded-xl hover:bg-white/5 transition-all"
                  style={{ border: "none", background: "transparent", cursor: "pointer", fontFamily: "inherit" }}
                >
                  {item}
                </button>
              ) : (
                <a
                  key={item}
                  href={`#${item.toLowerCase().replace(" ", "-")}`}
                  className="w-full text-left px-4 py-3 text-sm font-medium text-gray-300 hover:text-white rounded-xl hover:bg-white/5 transition-all block"
                  onClick={() => setMobileMenuOpen(false)}
                >
                  {item}
                </a>
              )
            )}
            <div style={{ paddingTop: "1rem", marginTop: "0.5rem", borderTop: "1px solid rgba(255,255,255,0.08)" }}>
              <button
                onClick={onLoginClick}
                style={{
                  width: "100%",
                  padding: "0.875rem",
                  borderRadius: "0.75rem",
                  fontWeight: 600,
                  fontSize: "0.875rem",
                  background: "rgba(255,255,255,0.02)",
                  backdropFilter: "blur(8px)",
                  color: "white",
                  border: "1px solid rgba(255,255,255,0.2)",
                  boxShadow: "inset 0 1px 0 rgba(255,255,255,0.15)",
                  cursor: "pointer",
                  transition: "all 0.2s",
                }}
              >
                Sign In
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </nav>
  );
};