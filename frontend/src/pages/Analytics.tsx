import React from 'react';
import { GlassCard } from '../components/GlassCard';
import { 
  ResponsiveContainer, 
  AreaChart, 
  Area, 
  XAxis, 
  YAxis, 
  Tooltip, 
  BarChart, 
  Bar, 
  LineChart, 
  Line
} from 'recharts';
import { TrendingUp, Award, Activity, BarChart2 } from 'lucide-react';

export const Analytics: React.FC = () => {
  
  // Simulated stats tracking records over time
  const accuracyData = [
    { name: 'Run 1', intent: 88, entity: 82, workflow: 85, success: 90 },
    { name: 'Run 2', intent: 90, entity: 85, workflow: 88, success: 92 },
    { name: 'Run 3', intent: 92, entity: 87, workflow: 91, success: 94 },
    { name: 'Run 4', intent: 91, entity: 89, workflow: 90, success: 93 },
    { name: 'Run 5', intent: 94, entity: 90, workflow: 93, success: 96 },
    { name: 'Run 6', intent: 95, entity: 92, workflow: 94, success: 98 }
  ];

  return (
    <div className="space-y-6">
      {/* Top Banner KPIs */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <GlassCard>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-violet-500/10 text-violet-500 border border-violet-500/20">
              <Award className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Intent Accuracy</span>
              <span className="text-xl font-extrabold text-slate-700 dark:text-slate-200 mt-0.5 block">95.3%</span>
            </div>
          </div>
        </GlassCard>
        <GlassCard>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-emerald-500/10 text-emerald-500 border border-emerald-500/20">
              <Activity className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">NER Recall F1</span>
              <span className="text-xl font-extrabold text-slate-700 dark:text-slate-200 mt-0.5 block">92.1%</span>
            </div>
          </div>
        </GlassCard>
        <GlassCard>
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-blue-500/10 text-blue-500 border border-blue-500/20">
              <TrendingUp className="w-5 h-5" />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider block">Mean Execution Speed</span>
              <span className="text-xl font-extrabold text-slate-700 dark:text-slate-200 mt-0.5 block">3.4 seconds</span>
            </div>
          </div>
        </GlassCard>
      </div>

      {/* Main Analytics charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        
        {/* Intent Classification Accuracy Area Chart */}
        <GlassCard className="h-[360px] flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <BarChart2 className="w-4 h-4 text-violet-500" />
              Intent Classification Accuracy
            </h4>
            <span className="text-[10px] text-slate-400 font-semibold block mt-0.5">
              Ratio of correctly matches verified against golden test datasets.
            </span>
          </div>

          <div className="flex-1 w-full min-h-[220px] mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={accuracyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorIntent" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} domain={[50, 100]} />
                <Tooltip contentStyle={{ background: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '11px' }} />
                <Area type="monotone" dataKey="intent" stroke="#8b5cf6" strokeWidth={2} fillOpacity={1} fill="url(#colorIntent)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Entity Extraction F1 area chart */}
        <GlassCard className="h-[360px] flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <BarChart2 className="w-4 h-4 text-emerald-500" />
              Named Entity Extraction (NER) F1 Score
            </h4>
            <span className="text-[10px] text-slate-400 font-semibold block mt-0.5">
              F1 performance tracking mapping recipients, dates, files, and URLs.
            </span>
          </div>

          <div className="flex-1 w-full min-h-[220px] mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={accuracyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorEntity" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#10b981" stopOpacity={0.2}/>
                    <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} domain={[50, 100]} />
                <Tooltip contentStyle={{ background: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '11px' }} />
                <Area type="monotone" dataKey="entity" stroke="#10b981" strokeWidth={2} fillOpacity={1} fill="url(#colorEntity)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Workflow Gen Accuracy */}
        <GlassCard className="h-[360px] flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <BarChart2 className="w-4 h-4 text-blue-500" />
              Workflow Schema Generation Accuracy
            </h4>
            <span className="text-[10px] text-slate-400 font-semibold block mt-0.5">
              Validation correctness of structured DAG topologies against ground truth.
            </span>
          </div>

          <div className="flex-1 w-full min-h-[220px] mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={accuracyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} domain={[50, 100]} />
                <Tooltip contentStyle={{ background: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '11px' }} />
                <Bar dataKey="workflow" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>

        {/* Task Success Rate line graph */}
        <GlassCard className="h-[360px] flex flex-col justify-between">
          <div>
            <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 flex items-center gap-1.5">
              <BarChart2 className="w-4 h-4 text-indigo-500" />
              Task Execution Success Rate
            </h4>
            <span className="text-[10px] text-slate-400 font-semibold block mt-0.5">
              Reliability curve showing percentage of successfully finished pipelines.
            </span>
          </div>

          <div className="flex-1 w-full min-h-[220px] mt-4">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={accuracyData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <XAxis dataKey="name" stroke="#94a3b8" fontSize={10} tickLine={false} />
                <YAxis stroke="#94a3b8" fontSize={10} tickLine={false} domain={[70, 100]} />
                <Tooltip contentStyle={{ background: '#1e293b', border: 'none', borderRadius: '8px', color: '#fff', fontSize: '11px' }} />
                <Line type="monotone" dataKey="success" stroke="#6366f1" strokeWidth={3.5} activeDot={{ r: 6 }} />
              </LineChart>
            </ResponsiveContainer>
          </div>
        </GlassCard>
      </div>
    </div>
  );
};
