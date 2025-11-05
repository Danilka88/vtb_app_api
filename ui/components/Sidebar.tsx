import React from 'react';
import { Logo, SparklesIcon } from '../constants';
import { ActiveView, NavItem } from '../types';

interface SidebarProps {
  navItems: NavItem[];
  activeView: ActiveView;
  setActiveView: (view: ActiveView) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ navItems, activeView, setActiveView }) => {
  return (
    <aside className="hidden lg:flex flex-col w-64 bg-slate-800/50 backdrop-blur-sm fixed top-0 left-0 h-full border-r border-slate-700/50">
      <div className="flex items-center gap-2 h-20 px-6 border-b border-slate-700/50">
        <Logo />
        <h1 className="text-xl font-bold text-white">Мультибанк</h1>
      </div>
      <nav className="flex-1 px-4 py-6 space-y-2">
        {navItems.map((item) => (
          <a
            key={item.id}
            href="#"
            onClick={(e) => {
              e.preventDefault();
              setActiveView(item.id);
            }}
            className={`flex items-center gap-3 px-4 py-2.5 rounded-lg transition-all duration-200 ${
              activeView === item.id
                ? 'bg-blue-600 text-white shadow-lg'
                : 'text-slate-400 hover:bg-slate-700/50 hover:text-white'
            }`}
          >
            {item.icon}
            <span className="font-medium">{item.label}</span>
          </a>
        ))}
      </nav>
    </aside>
  );
};
