import { lazy, Suspense } from "react";
import { Routes, Route, Navigate, useLocation } from "react-router-dom";
import { AnimatePresence, motion } from "motion/react";
import FluidBackground from "./components/ui/FluidBackground";
import { IlluminatedHero } from "./components/ui/illuminated-hero";
import { Navbar } from "./components/layout/Navbar";
import { Footer } from "./components/layout/Footer";
import { SocialProof } from "./components/sections/SocialProof";
import { Features } from "./components/sections/Features";
import { UseCases } from "./components/sections/UseCases";
import { ValueProp } from "./components/sections/ValueProp";
import { FAQ } from "./components/sections/FAQ";
import { Pricing } from "./components/sections/Pricing";
import { SVGFilters } from "./components/ui/SVGFilters";
import { useNavigate } from "react-router-dom";

const LoginScreen = lazy(() => import("./components/screens/LoginScreen"));
const AppView = lazy(() => import("./components/screens/AppView"));
const GenericPage = lazy(() => import("./components/screens/GenericPage"));

const genericPaths = [
  '/integrations', '/changelog', '/documentation', '/api-reference', 
  '/community', '/support', '/blog', '/about-us', '/careers', 
  '/privacy-policy', '/terms-of-service', '/contact'
];

// ─── Loading fallback ────────────────────────────────────────────────────────
const LoadingFallback = () => (
  <div className="min-h-screen flex items-center justify-center bg-[#020202]">
    <motion.div
      animate={{ opacity: [0.3, 1, 0.3] }}
      transition={{ duration: 1.5, repeat: Infinity, ease: "easeInOut" }}
      className="flex flex-col items-center gap-4"
    >
      <div className="w-10 h-10 rounded-xl border border-indigo-500/40 bg-indigo-500/10 flex items-center justify-center">
        <div className="w-4 h-4 rounded-full bg-indigo-400 animate-ping" />
      </div>
      <p className="text-[10px] font-mono text-indigo-400 uppercase tracking-[0.3em]">
        Initializing Module...
      </p>
    </motion.div>
  </div>
);

// ─── Landing View ────────────────────────────────────────────────────────────
const LandingView = () => {
  const navigate = useNavigate();
  return (
    <>
      <Navbar
        onLoginClick={() => navigate("/login")}
        onDashboardClick={() => navigate("/login")}
      />
      <main id="home">
        <IlluminatedHero />
        <SocialProof />
        <Features />
        <UseCases />
        <ValueProp />
        <Pricing />
        <FAQ />
      </main>
      <Footer />
    </>
  );
};

// ─── Animated route wrapper ───────────────────────────────────────────────────
const AnimatedRoute = ({ children }: { children: React.ReactNode }) => {
  const location = useLocation();
  return (
    <AnimatePresence mode="wait" initial={false}>
      <motion.div
        key={location.pathname}
        initial={{ opacity: 0, y: 20, filter: "blur(8px)" }}
        animate={{ opacity: 1, y: 0, filter: "blur(0px)" }}
        exit={{ opacity: 0, y: -12, filter: "blur(4px)" }}
        transition={{ duration: 0.4, ease: "easeOut" }}
        className="w-full"
      >
        {children}
      </motion.div>
    </AnimatePresence>
  );
};

// ─── Root App ────────────────────────────────────────────────────────────────
export default function App() {
  const location = useLocation();

  return (
    <div className="min-h-screen bg-[#020202] font-sans text-gray-100 selection:bg-indigo-500/30 selection:text-indigo-200">
      <SVGFilters />
      <FluidBackground />

      <div className="relative min-h-screen overflow-hidden bg-black/10 backdrop-blur-[1px]">
        <Suspense fallback={<LoadingFallback />}>
          <AnimatePresence mode="wait" initial={false}>
            <Routes location={location} key={location.pathname}>
              <Route
                path="/"
                element={
                  <AnimatedRoute>
                    <LandingView />
                  </AnimatedRoute>
                }
              />
              <Route
                path="/login"
                element={
                  <AnimatedRoute>
                    <LoginScreen
                      onLogin={() => {}}
                      onBack={() => {}}
                    />
                  </AnimatedRoute>
                }
              />
              {genericPaths.map(path => (
                <Route
                  key={path}
                  path={path}
                  element={
                    <AnimatedRoute>
                      <GenericPage />
                    </AnimatedRoute>
                  }
                />
              ))}
              <Route path="/app/*" element={<AppView />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </AnimatePresence>
        </Suspense>
      </div>
    </div>
  );
}
