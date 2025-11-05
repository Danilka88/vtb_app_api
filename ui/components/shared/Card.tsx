
import React from 'react';

interface CardProps {
  children: React.ReactNode;
  className?: string;
}

export const Card: React.FC<CardProps> = ({ children, className = '' }) => {
  return (
    <div className={`bg-slate-800/50 border border-slate-700/50 rounded-2xl shadow-lg backdrop-blur-sm ${className}`}>
      {children}
    </div>
  );
};
