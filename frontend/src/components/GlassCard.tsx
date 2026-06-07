import React from 'react';

interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  glow?: 'none' | 'violet' | 'indigo';
  hover?: boolean;
}

export const GlassCard: React.FC<GlassCardProps> = ({
  children,
  className = '',
  glow = 'none',
  hover = false
}) => {
  const glowClass = 
    glow === 'violet' ? 'neon-glow-violet' :
    glow === 'indigo' ? 'neon-glow-indigo' : '';

  const hoverClass = hover ? 'hover-3d' : '';

  return (
    <div className={`glass-card rounded-2xl p-6 border ${glowClass} ${hoverClass} ${className}`}>
      {children}
    </div>
  );
};
