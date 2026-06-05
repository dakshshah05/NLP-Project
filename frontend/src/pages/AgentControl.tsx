import React, { useEffect, useState } from 'react';
import { GlassCard } from '../components/GlassCard';
import type { Agent } from '../types';
import { 
  Bot, 
  Cpu, 
  FileText, 
  Mail, 
  Globe, 
  FolderOpen, 
  Database,
  ToggleLeft,
  ToggleRight,
  TrendingUp
} from 'lucide-react';

import { useAuth } from '../context/AuthContext';

export const AgentControl: React.FC = () => {
  const { token } = useAuth();
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchAgents = async () => {
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${backendUrl}/api/agents`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setAgents(data);
      }
    } catch (err) {
      console.error('Failed to load agents', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchAgents();
      const interval = setInterval(fetchAgents, 5000);
      return () => clearInterval(interval);
    }
  }, [token]);

  const handleToggleAgent = async (name: string, currentStatus: string) => {
    const nextStatus = currentStatus === 'Disabled' ? 'Idle' : 'Disabled';
    
    // Optimistic UI update
    setAgents((prev) => 
      prev.map((a) => (a.name === name ? { ...a, status: nextStatus } : a))
    );

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      await fetch(`${backendUrl}/api/agents/${name}/toggle`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ status: nextStatus }),
      });
      fetchAgents();
    } catch (err) {
      console.error('Error toggling agent status', err);
    }
  };

  const getAgentIcon = (name: string) => {
    switch (name) {
      case 'Planner Agent': return Cpu;
      case 'Document Agent': return FileText;
      case 'Email Agent': return Mail;
      case 'Browser Agent': return Globe;
      case 'File Agent': return FolderOpen;
      case 'Memory Agent': return Database;
      default: return Bot;
    }
  };

  if (loading && agents.length === 0) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="w-10 h-10 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents.map((agent) => {
          const Icon = getAgentIcon(agent.name);
          const isEnabled = agent.status !== 'Disabled';
          
          let statusBadgeColor = 'bg-slate-500/10 text-slate-500 border-slate-500/20';
          if (agent.status === 'Active') {
            statusBadgeColor = 'bg-violet-500/10 text-violet-500 border-violet-500/20 animate-pulse';
          } else if (agent.status === 'Idle') {
            statusBadgeColor = 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20';
          }

          return (
            <GlassCard 
              key={agent.name} 
              hover 
              className={`flex flex-col justify-between ${!isEnabled ? 'opacity-65' : ''}`}
            >
              <div>
                {/* Card Title & Toggle Switch */}
                <div className="flex items-center justify-between pb-3 border-b border-slate-200/50 dark:border-white/5 mb-4">
                  <div className="flex items-center gap-2.5">
                    <div className={`p-2 rounded-xl border ${
                      isEnabled ? 'text-violet-500 bg-violet-500/10 border-violet-500/20' : 'text-slate-400 bg-slate-100 dark:bg-white/5 border-slate-200/20'
                    }`}>
                      <Icon className="w-5 h-5" />
                    </div>
                    <div>
                      <h4 className="text-sm font-bold text-slate-800 dark:text-slate-100">{agent.name}</h4>
                      <span className="text-[9px] text-slate-400 font-semibold uppercase">Micro-Agent</span>
                    </div>
                  </div>

                  <button
                    onClick={() => handleToggleAgent(agent.name, agent.status)}
                    className="focus:outline-none"
                    title={isEnabled ? "Disable Agent" : "Enable Agent"}
                  >
                    {isEnabled ? (
                      <ToggleRight className="w-8 h-8 text-violet-600 cursor-pointer" />
                    ) : (
                      <ToggleLeft className="w-8 h-8 text-slate-400 cursor-pointer" />
                    )}
                  </button>
                </div>

                {/* Metrics */}
                <div className="grid grid-cols-2 gap-3 mb-5">
                  <div className="p-3 bg-slate-100/20 dark:bg-white/5 border border-slate-200/30 rounded-2xl text-center">
                    <span className="text-[9px] text-slate-400 block uppercase font-bold">Tasks Finished</span>
                    <span className="text-lg font-extrabold text-slate-700 dark:text-slate-200 mt-1 block">
                      {agent.tasks_completed}
                    </span>
                  </div>
                  <div className="p-3 bg-slate-100/20 dark:bg-white/5 border border-slate-200/30 rounded-2xl text-center">
                    <span className="text-[9px] text-slate-400 block uppercase font-bold flex items-center justify-center gap-0.5">
                      <TrendingUp className="w-3 h-3 text-emerald-500" /> Success Rate
                    </span>
                    <span className="text-lg font-extrabold text-slate-700 dark:text-slate-200 mt-1 block">
                      {agent.success_rate}%
                    </span>
                  </div>
                </div>

                {/* Capabilities */}
                <div>
                  <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block mb-2">Capabilities</span>
                  <div className="flex flex-wrap gap-1.5">
                    {agent.capabilities.map((cap, i) => (
                      <span 
                        key={i} 
                        className="text-[9px] font-semibold bg-slate-100 dark:bg-white/5 text-slate-600 dark:text-slate-300 border border-slate-200/30 px-2 py-0.5 rounded-full"
                      >
                        {cap}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Status footer */}
              <div className="mt-5 pt-3 border-t border-slate-200/50 dark:border-white/5 flex items-center justify-between text-xs">
                <span className="text-slate-400 font-medium">Status</span>
                <span className={`px-2 py-0.5 rounded-full border text-[9px] font-bold uppercase tracking-wider ${statusBadgeColor}`}>
                  {agent.status}
                </span>
              </div>
            </GlassCard>
          );
        })}
      </div>
    </div>
  );
};
