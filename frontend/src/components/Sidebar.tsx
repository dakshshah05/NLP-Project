import React from 'react';
import { 
  LayoutDashboard, 
  Terminal, 
  Sparkles, 
  GitFork, 
  Bot, 
  Activity, 
  Database, 
  BarChart3, 
  BookOpen,
  Cpu
} from 'lucide-react';

interface SidebarProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

export const Sidebar: React.FC<SidebarProps> = ({ activeTab, setActiveTab }) => {
  const menuItems = [
    { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { id: 'command-center', label: 'AI Command Center', icon: Terminal },
    { id: 'nlp-analysis', label: 'NLP Analysis', icon: Sparkles },
    { id: 'workflow-builder', label: 'Workflow Builder', icon: GitFork },
    { id: 'agent-control', label: 'Agent Control Center', icon: Bot },
    { id: 'execution-monitor', label: 'Execution Monitor', icon: Activity },
    { id: 'memory-center', label: 'Memory Center', icon: Database },
    { id: 'analytics', label: 'Analytics Dashboard', icon: BarChart3 },
    { id: 'research', label: 'Research Page', icon: BookOpen },
  ];

  return (
    <aside className="w-72 hidden lg:flex flex-col h-screen fixed left-0 top-0 border-r border-slate-200/50 dark:border-white/5 glass-panel z-20 transition-all duration-300">
      {/* Brand Header */}
      <div className="p-6 border-b border-slate-200/50 dark:border-white/5 flex items-center gap-3">
        <div className="p-2 rounded-xl bg-violet-600/10 text-violet-500 border border-violet-500/20">
          <Cpu className="w-6 h-6 animate-pulse-slow" />
        </div>
        <div>
          <h1 className="font-bold text-lg leading-none tracking-wide bg-gradient-to-r from-violet-600 to-indigo-500 bg-clip-text text-transparent dark:from-violet-400 dark:to-indigo-400">
            AURA AI
          </h1>
          <span className="text-[10px] uppercase font-semibold text-slate-500 dark:text-slate-400 tracking-wider">
            Autonomous Agent
          </span>
        </div>
      </div>

      {/* Navigation List */}
      <nav className="flex-1 p-4 overflow-y-auto space-y-1">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = activeTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => setActiveTab(item.id)}
              className={`w-full flex items-center gap-3.5 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200 ${
                isActive
                  ? 'bg-violet-600 text-white shadow-lg shadow-violet-500/20 scale-[1.02]'
                  : 'text-slate-700 dark:text-slate-300 hover:bg-slate-200/40 dark:hover:bg-white/5'
              }`}
            >
              <Icon className={`w-5 h-5 ${isActive ? 'text-white' : 'text-slate-500 dark:text-slate-400 group-hover:text-violet-500'}`} />
              {item.label}
            </button>
          );
        })}
      </nav>

      {/* System Status footer */}
      <div className="p-4 border-t border-slate-200/50 dark:border-white/5 bg-slate-100/30 dark:bg-black/10">
        <div className="flex items-center justify-between text-xs text-slate-500 dark:text-slate-400 mb-1">
          <span>Engine Status</span>
          <span className="flex items-center gap-1.5 font-semibold text-emerald-500">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping" />
            Online
          </span>
        </div>
        <div className="text-[10px] text-slate-500 dark:text-slate-400/80 mt-1">
          v1.4.0 (FastAPI + React)
        </div>
      </div>
    </aside>
  );
};
