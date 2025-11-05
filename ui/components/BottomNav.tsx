
import React from 'react';
import { ActiveView, NavItem } from '../types';

interface BottomNavProps {
  navItems: NavItem[];
  activeView: ActiveView;
  setActiveView: (view: ActiveView) => void;
}

export const BottomNav: React.FC<BottomNavProps> = ({ navItems, activeView, setActiveView }) => {
  return (
    <nav className="lg:hidden fixed bottom-0 left-0 right-0 bg-slate-800/80 backdrop-blur-xl border-t border-slate-700/50 flex justify-around p-2 z-50">
      {navItems.slice(0, 5).map((item) => (
        <button
          key={item.id}
          onClick={() => setActiveView(item.id)}
          className={`flex flex-col items-center justify-center w-16 h-16 rounded-lg transition-all duration-200 ${
            activeView === item.id
              ? 'text-blue-400'
              : 'text-slate-400 hover:text-white'
          }`}
        >
          {item.icon}
          <span className="text-xs mt-1">{item.label}</span>
        </button>
      ))}
    </nav>
  );
};
