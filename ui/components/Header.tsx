
import React from 'react';
import { BellIcon, PlusCircleIcon, UserCircleIcon } from '../constants';

export const Header: React.FC = () => {
  return (
    <header className="flex items-center justify-between h-20 px-4 md:px-8 border-b border-slate-700/50 bg-slate-900/50 backdrop-blur-sm sticky top-0 z-40">
       <div className="flex items-center gap-4">
        <UserCircleIcon className="w-10 h-10 text-slate-400" />
        <div>
          <h2 className="text-lg font-semibold text-white">С возвращением!</h2>
          <p className="text-sm text-slate-400">Вот ваш финансовый обзор.</p>
        </div>
      </div>
      <div className="flex items-center gap-4">
        <button className="p-2 rounded-full hover:bg-slate-700/50 text-slate-400 hover:text-white transition">
          <BellIcon className="w-6 h-6" />
        </button>
        <button className="hidden sm:flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition shadow-lg">
          <PlusCircleIcon className="w-5 h-5" />
          <span>Добавить счет</span>
        </button>
      </div>
    </header>
  );
};
