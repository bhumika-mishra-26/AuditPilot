import React from 'react';

interface CyberCardProps {
  title: string;
  subtitle: string;
  highlight: string;
  description: string;
  prompt?: string;
}

export default function CyberCard({ title, subtitle, highlight, description, prompt = "HOVER ME" }: CyberCardProps) {
  return (
    <div className="cyber-container noselect mx-auto">
      <div className="cyber-canvas">
        {/* Trackers for 3D effect */}
        {[...Array(25)].map((_, i) => (
          <div key={i} className={`cyber-tracker cyber-tr-${i + 1}`} />
        ))}
        
        <div id="cyber-card">
          <div className="cyber-card-content p-6 flex flex-col items-center justify-center text-center">
            <div className="cyber-card-glare"></div>
            <div className="cyber-cyber-lines">
              <span></span><span></span><span></span><span></span>
            </div>
            <p id="cyber-prompt">{prompt}</p>
            
            <div className="cyber-title mb-2" dangerouslySetInnerHTML={{ __html: title }}></div>
            
            <div className="cyber-description opacity-0 transition-opacity duration-300 group-hover:opacity-100 text-xs text-gray-400 mb-4 px-4">
              {description}
            </div>

            <div className="cyber-glowing-elements">
              <div className="cyber-glow-1"></div>
              <div className="cyber-glow-2"></div>
              <div className="cyber-glow-3"></div>
            </div>
            <div className="cyber-subtitle">
              <span>{subtitle}</span>
              <span className="cyber-highlight">{highlight}</span>
            </div>
            <div className="cyber-card-particles">
              <span></span><span></span><span></span><span></span><span></span><span></span>
            </div>
            <div className="cyber-corner-elements">
              <span></span><span></span><span></span><span></span>
            </div>
            <div className="cyber-scan-line"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
