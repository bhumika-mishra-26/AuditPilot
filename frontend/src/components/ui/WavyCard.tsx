import React from 'react';
import { cn } from "../../lib/utils";

interface WavyCardProps {
  children: React.ReactNode;
  className?: string;
  containerClassName?: string;
  color?: string; // e.g., "rgb(6, 182, 212)" or "#8b5cf6"
  filterId?: string; // id of the SVG filter to use
  glowColor?: string; // optional gradient glow color
  key?: React.Key;
}

export default function WavyCard({
  children,
  className,
  containerClassName,
  color = "rgb(6, 182, 212)",
  filterId = "turbulent-displace-teal",
  glowColor
}: WavyCardProps) {
  const baseGlow = glowColor || color;

  return (
    <div className={cn("relative group transition-transform duration-300 hover:scale-[1.02] flex flex-col", containerClassName)}>
      {/* Background/Outer Glow */}
      <div 
        className="absolute inset-0 rounded-[20px] transform scale(1.08) filter blur(24px) opacity-20 -z-10"
        style={{ 
          background: `linear-gradient(-30deg, ${baseGlow}, transparent, ${baseGlow})` 
        }}
      />

      <div className="relative isolate flex-1 flex flex-col" style={{ borderRadius: '20px' }}>
        {/* Layered Borders */}
        <div className="absolute inset-0 pointer-events-none rounded-[20px] isolate">
          {/* Wave Border (using SVG filter) - optimized to composite separately */}
          <div 
            className="absolute inset-0 box-border pointer-events-none border-2 border-solid" 
            style={{ 
              borderRadius: '20px', 
              borderColor: color, 
              filter: `url("#${filterId}")`,
              willChange: 'filter'
            }} 
          />
          
          {/* Soft Glow Inner Border */}
          <div 
            className="absolute inset-0 box-border pointer-events-none border-2 border-solid" 
            style={{ 
              borderRadius: '20px', 
              borderColor: color.replace('rgb', 'rgba').replace(')', ', 0.4)'), 
              filter: 'blur(1.5px)', 
              opacity: 0.4,
              willChange: 'filter'
            }} 
          />
          
          {/* Blur Layer */}
          <div 
            className="absolute inset-0 box-border pointer-events-none border-2 border-solid" 
            style={{ 
              borderRadius: '20px', 
              borderColor: color, 
              filter: 'blur(4px)', 
              opacity: 0.3,
              willChange: 'filter'
            }} 
          />
        </div>

        {/* Content Wrapper */}
        <div className={cn("relative overflow-hidden rounded-[20px] h-full flex flex-col", className)}>
          {children}
        </div>
      </div>
    </div>
  );
}
