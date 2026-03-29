import React from "react";
import { motion } from "motion/react";

export default function FluidBackground() {
  return (
    <div className="fixed inset-0 -z-10 bg-[#020202] overflow-hidden">
      {/* Animated Fluid Waves - Increased Opacity and Vibrancy */}
      <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
        <motion.div
          animate={{
            scale: [1, 1.3, 1],
            rotate: [0, 90, 0],
            x: [-150, 150, -150],
            y: [-100, 100, -100],
          }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
          style={{ backgroundImage: 'radial-gradient(circle, rgba(99, 102, 241, 0.25) 0%, rgba(99, 102, 241, 0) 65%)', willChange: 'transform' }}
          className="absolute w-[1200px] h-[1200px] rounded-full"
        />
        <motion.div
          animate={{
            scale: [1.3, 1, 1.3],
            rotate: [-45, 45, -45],
            x: [150, -150, 150],
            y: [100, -100, 100],
          }}
          transition={{ duration: 18, repeat: Infinity, ease: "easeInOut" }}
          style={{ backgroundImage: 'radial-gradient(circle, rgba(96, 165, 250, 0.2) 0%, rgba(96, 165, 250, 0) 65%)', willChange: 'transform' }}
          className="absolute w-[1100px] h-[1100px] rounded-full"
        />
        <motion.div
          animate={{
            scale: [1, 1.2, 1],
            x: [0, 100, 0],
            y: [150, -150, 150],
          }}
          transition={{ duration: 12, repeat: Infinity, ease: "easeInOut" }}
          style={{ backgroundImage: 'radial-gradient(circle, rgba(251, 146, 60, 0.15) 0%, rgba(251, 146, 60, 0) 65%)', willChange: 'transform' }}
          className="absolute w-[900px] h-[900px] rounded-full"
        />
      </div>

      {/* Vertical Bars Overlay - More Pronounced */}
      <div 
        className="absolute inset-0 opacity-[0.25]"
        style={{
          backgroundImage: `linear-gradient(to right, rgba(0,0,0,0) 0%, rgba(0,0,0,0) 50%, rgba(0,0,0,1) 50%, rgba(0,0,0,1) 100%)`,
          backgroundSize: '8px 100%'
        }}
      />

      {/* Subtle Grid */}
      <div 
        className="absolute inset-0 opacity-[0.08]"
        style={{
          backgroundImage: `linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px)`,
          backgroundSize: '50px 50px'
        }}
      />
      
      {/* Vignette */}
      <div className="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-black/60" />
    </div>
  );
}
