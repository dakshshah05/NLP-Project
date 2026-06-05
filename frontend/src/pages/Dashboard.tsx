import React, { useEffect, useState } from 'react';
import { GlassCard } from '../components/GlassCard';
import { 
  Command, 
  CheckCircle, 
  Cpu, 
  TrendingUp, 
  Terminal, 
  Play, 
  AlertTriangle 
} from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, Tooltip } from 'recharts';
import type { DashboardStats } from '../types';
import { useAuth } from '../context/AuthContext';

export const Dashboard: React.FC = () => {
  const { token } = useAuth();
  const [stats, setStats] = useState<DashboardStats | null>(null);
  const [loading, setLoading] = useState(true);

  const fetchStats = async () => {
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${backendUrl}/api/dashboard/stats`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setStats(data);
      }
    } catch (err) {
      console.error('Failed to fetch dashboard stats', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchStats();
    const interval = setInterval(fetchStats, 4000);
    return () => clearInterval(interval);
  }, []);

  if (loading || !stats) {
    return (
      <div className="flex items-center justify-center min-h-[500px]">
        <div className="w-10 h-10 border-4 border-violet-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  const kpis = [
    { label: 'Total Commands', value: stats.total_commands, icon: Command, color: 'text-violet-500 bg-violet-500/10' },
    { label: 'Tasks Completed', value: stats.tasks_completed, icon: CheckCircle, color: 'text-emerald-500 bg-emerald-500/10' },
    { label: 'Active Agents', value: stats.active_agents, icon: Cpu, color: 'text-blue-500 bg-blue-500/10' },
    { label: 'Success Rate', value: `${stats.success_rate}%`, icon: TrendingUp, color: 'text-indigo-500 bg-indigo-500/10' },
  ];

  // Recharts workflow chart format
  const chartData = [
    { name: 'Pending', count: stats.workflow_stats.pending, fill: '#64748b' },
    { name: 'Running', count: stats.workflow_stats.running, fill: '#8b5cf6' },
    { name: 'Completed', count: stats.workflow_stats.completed, fill: '#10b981' },
    { name: 'Failed', count: stats.workflow_stats.failed, fill: '#ef4444' }
  ];

  return (
    <div className="space-y-6">
      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {kpis.map((kpi, idx) => {
          const Icon = kpi.icon;
          return (
            <GlassCard key={idx} hover glow={idx === 0 ? 'violet' : 'none'}>
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-xs font-semibold text-slate-400 dark:text-slate-400 uppercase tracking-wider">
                    {kpi.label}
                  </p>
                  <h3 className="text-3xl font-extrabold mt-1 tracking-tight text-slate-800 dark:text-white">
                    {kpi.value}
                  </h3>
                </div>
                <div className={`p-3 rounded-xl border border-slate-200/20 ${kpi.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            </GlassCard>
          );
        })}
      </div>

      {/* Main Charts & Activity Logs */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Workflow Stats Chart */}
        <GlassCard className="lg:col-span-7 flex flex-col h-[400px]">
          <h4 className="text-md font-bold mb-4 text-slate-800 dark:text-slate-200">
            Workflow Process Statistics
          </h4>
          <div className="flex-1 w-full min-h-[280px]">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={11} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={11} tickLine={false} />
                <Tooltip 
                  cursor={{ fill: 'rgba(255,255,255,0.03)' }}
                  contentStyle={{ 
                    background: '#1e293b', 
                    borderRadius: '8px', 
                    border: 'none',
                    color: '#fff',
                    fontSize: '12px'
                  }} 
                />
                <Bar dataKey="count" radius={[8, 8, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Recent Activities list */}
        <GlassCard className="lg:col-span-5 flex flex-col h-[400px]">
          <h4 className="text-md font-bold mb-4 text-slate-800 dark:text-slate-200">
            Recent Activities
          </h4>
          
          <div className="flex-1 overflow-y-auto space-y-3 pr-1">
            {stats.recent_activities.length === 0 ? (
              <div className="text-center text-xs text-slate-400 py-8">
                No activity detected. Execute a command to begin.
              </div>
            ) : (
              stats.recent_activities.map((act) => {
                let ActIcon = Terminal;
                let colorClass = 'text-violet-500 bg-violet-500/10 border-violet-500/20';
                
                if (act.type === 'execution') {
                  if (act.description.includes('completed')) {
                    ActIcon = CheckCircle;
                    colorClass = 'text-emerald-500 bg-emerald-500/10 border-emerald-500/20';
                  } else if (act.description.includes('failed')) {
                    ActIcon = AlertTriangle;
                    colorClass = 'text-red-500 bg-red-500/10 border-red-500/20';
                  } else {
                    ActIcon = Play;
                    colorClass = 'text-blue-500 bg-blue-500/10 border-blue-500/20';
                  }
                }

                return (
                  <div 
                    key={act.id} 
                    className="flex gap-3 p-3 rounded-xl border border-slate-200/50 dark:border-white/5 bg-slate-100/20 dark:bg-white/5 hover:bg-slate-100/50 dark:hover:bg-white/10 transition-colors"
                  >
                    <div className={`p-2 rounded-lg border flex items-center justify-center shrink-0 ${colorClass}`}>
                      <ActIcon className="w-4 h-4" />
                    </div>
                    <div className="flex-1 min-w-0">
                      <p className="text-xs font-semibold text-slate-700 dark:text-slate-200 truncate">
                        {act.description}
                      </p>
                      <span className="text-[10px] text-slate-400 mt-0.5 block">
                        {new Date(act.timestamp).toLocaleTimeString()}
                      </span>
                    </div>
                  </div>
                );
              })
            )}
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
