import React, { useState } from 'react';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon, Bell, Menu, X, Cpu } from 'lucide-react';

interface HeaderProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Header: React.FC<HeaderProps> = ({ activeTab, setActiveTab }) => {
  const { theme, toggleTheme } = useTheme();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const formatTitle = (tab: string) => {
    return tab
      .split('-')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  };

  const menuItems = [
    { id: 'dashboard', label: 'Dashboard' },
    { id: 'command-center', label: 'AI Command Center' },
    { id: 'nlp-analysis', label: 'NLP Analysis' },
    { id: 'workflow-builder', label: 'Workflow Builder' },
    { id: 'agent-control', label: 'Agent Control Center' },
    { id: 'execution-monitor', label: 'Execution Monitor' },
    { id: 'memory-center', label: 'Memory Center' },
    { id: 'analytics', label: 'Analytics Dashboard' },
    { id: 'research', label: 'Research Page' },
  ];

  return (
    <>
      <header className="h-20 border-b border-slate-200/50 dark:border-white/5 glass-panel fixed top-0 right-0 left-0 lg:left-72 z-10 flex items-center justify-between px-6 transition-all duration-300">
        {/* Left: Mobile Menu Trigger & Page Title */}
        <div className="flex items-center gap-4">
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="lg:hidden p-2 rounded-xl text-slate-500 hover:bg-slate-100 dark:hover:bg-white/5 transition-all"
          >
            <Menu className="w-6 h-6" />
          </button>
          
          <h2 className="text-xl font-bold tracking-tight text-slate-800 dark:text-white">
            {formatTitle(activeTab)}
          </h2>
        </div>

        {/* Right: Actions */}
        <div className="flex items-center gap-3">
          <div className="hidden sm:flex items-center gap-2 px-3 py-1.5 rounded-full bg-violet-500/10 border border-violet-500/20 text-xs text-violet-600 dark:text-violet-400 font-medium">
            <span className="w-1.5 h-1.5 rounded-full bg-violet-500 animate-ping" />
            Ollama Node Active
          </div>

          <button
            onClick={toggleTheme}
            className="p-2.5 rounded-xl border border-slate-200/50 dark:border-white/5 text-slate-500 hover:bg-slate-200/50 dark:hover:bg-white/5 transition-all"
            title="Toggle theme"
          >
            {theme === 'dark' ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-indigo-600" />}
          </button>

          <button
            className="p-2.5 rounded-xl border border-slate-200/50 dark:border-white/5 text-slate-500 hover:bg-slate-200/50 dark:hover:bg-white/5 transition-all relative"
            title="Notifications"
          >
            <Bell className="w-5 h-5" />
            <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-violet-600 rounded-full ring-2 ring-white dark:ring-[#0f1224]" />
          </button>
        </div>
      </header>

      {/* Mobile Sidebar overlay */}
      {mobileMenuOpen && (
        <div className="fixed inset-0 z-50 lg:hidden flex">
          <div className="fixed inset-0 bg-slate-900/60 backdrop-blur-sm" onClick={() => setMobileMenuOpen(false)} />
          
          <div className="w-72 bg-slate-50 dark:bg-[#0f101d] h-full relative z-10 flex flex-col p-6 shadow-2xl animate-in slide-in-from-left duration-250 border-r border-slate-200/50 dark:border-white/5">
            <div className="flex items-center justify-between mb-8">
              <div className="flex items-center gap-3">
                <Cpu className="w-6 h-6 text-violet-500 animate-pulse-slow" />
                <span className="font-bold text-lg text-slate-800 dark:text-white">AURA AI</span>
              </div>
              <button
                onClick={() => setMobileMenuOpen(false)}
                className="p-1 rounded-lg hover:bg-slate-200 dark:hover:bg-white/10"
              >
                <X className="w-6 h-6 text-slate-400" />
              </button>
            </div>

            <nav className="flex-1 space-y-1">
              {menuItems.map((item) => (
                <button
                  key={item.id}
                  onClick={() => {
                    setActiveTab(item.id);
                    setMobileMenuOpen(false);
                  }}
                  className={`w-full text-left px-4 py-3 rounded-xl text-sm font-medium transition-all ${
                    activeTab === item.id
                      ? 'bg-violet-600 text-white'
                      : 'text-slate-600 dark:text-slate-300 hover:bg-slate-200/50 dark:hover:bg-white/5'
                  }`}
                >
                  {item.label}
                </button>
              ))}
            </nav>
          </div>
        </div>
      )}
    </>
  );
};
