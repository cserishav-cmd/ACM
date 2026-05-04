import React from 'react';

export default function Logo({ className = "h-12", variant = "horizontal", showText = true }) {
  // variant: "horizontal" (icon + text side-by-side) or "vertical" (icon above text)
  
  return (
    <div className={`flex ${variant === 'vertical' ? 'flex-col' : 'flex-row'} items-center gap-3 ${className}`}>
      {/* SVG Icon */}
      <svg 
        viewBox="0 0 100 120" 
        className={`${variant === 'vertical' ? 'h-full' : 'h-full'} w-auto drop-shadow-sm`} 
        fill="none" 
        xmlns="http://www.w3.org/2000/svg"
      >
        {/* Leaf Shape Base */}
        <path 
          d="M50 5 C95 35, 95 85, 50 115 C5 85, 5 35, 50 5 Z" 
          fill="url(#leaf-grad)" 
        />
        
        {/* Geometric Tech Mesh Overlay */}
        <g stroke="#002202" strokeWidth="2" opacity="0.25" strokeLinecap="round" strokeLinejoin="round">
          {/* Vertical Center */}
          <line x1="50" y1="5" x2="50" y2="40" />
          {/* Inner Diamond */}
          <polygon points="50,40 25,55 50,75 75,55" fill="none" />
          {/* Outer connections */}
          <line x1="25" y1="55" x2="10" y2="60" />
          <line x1="75" y1="55" x2="90" y2="60" />
          <line x1="50" y1="75" x2="20" y2="90" />
          <line x1="50" y1="75" x2="80" y2="90" />
          <line x1="20" y1="90" x2="50" y2="115" />
          <line x1="80" y1="90" x2="50" y2="115" />
          <line x1="25" y1="55" x2="20" y2="90" />
          <line x1="75" y1="55" x2="80" y2="90" />
        </g>
        
        {/* Tech Nodes */}
        <g fill="#002202" opacity="0.6">
          <circle cx="50" cy="40" r="3" />
          <circle cx="25" cy="55" r="3" />
          <circle cx="75" cy="55" r="3" />
          <circle cx="50" cy="75" r="3" />
        </g>
        
        {/* Location Pin at Bottom */}
        <path 
          d="M50 70 C41 70 34 77 34 86 C34 98 50 115 50 115 C50 115 66 98 66 86 C66 77 59 70 50 70 Z" 
          fill="#002202" 
        />
        <circle cx="50" cy="84" r="5" fill="#FFFFFF" />

        <defs>
          <linearGradient id="leaf-grad" x1="0" y1="0" x2="100" y2="120" gradientUnits="userSpaceOnUse">
            <stop stopColor="#91d885" />
            <stop offset="0.4" stopColor="#2a6b27" />
            <stop offset="1" stopColor="#003300" />
          </linearGradient>
        </defs>
      </svg>
      
      {/* Text Branding */}
      {showText && (
        <div className={`flex flex-col ${variant === 'vertical' ? 'items-center mt-2' : 'items-start justify-center'}`}>
          <span 
            className="font-['Plus_Jakarta_Sans'] font-extrabold text-[#002202] dark:text-[#91d885] leading-none tracking-tight" 
            style={{ fontSize: variant === 'vertical' ? '1.5em' : '1.3em' }}
          >
            CROPCARE
          </span>
          <span 
            className="font-['Plus_Jakarta_Sans'] font-semibold text-slate-800 dark:text-slate-300 leading-none" 
            style={{ fontSize: variant === 'vertical' ? '0.85em' : '0.7em', marginTop: '0.25em' }}
          >
            Smart Farm Solutions
          </span>
        </div>
      )}
    </div>
  );
}
