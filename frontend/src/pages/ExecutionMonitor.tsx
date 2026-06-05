import React, { useEffect, useState, useRef } from 'react';
import { GlassCard } from '../components/GlassCard';
import type { Workflow, WorkflowNode, ExecutionLog } from '../types';
import { 
  Activity, 
  Terminal, 
  Clock, 
  CheckCircle, 
  AlertCircle, 
  Loader
} from 'lucide-react';

import { useAuth } from '../context/AuthContext';

interface ExecutionMonitorProps {
  activeWorkflow: Workflow | null;
}

export const ExecutionMonitor: React.FC<ExecutionMonitorProps> = ({ activeWorkflow }) => {
  const { token } = useAuth();
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [logs, setLogs] = useState<ExecutionLog[]>([]);
  const [status, setStatus] = useState<string>('Pending');
  const [executionId, setExecutionId] = useState<string>('');
  const [selectedWorkflowId, setSelectedWorkflowId] = useState<string>('');
  const logTerminalRef = useRef<HTMLDivElement>(null);

  const fetchStatus = async (wfId: string) => {
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${backendUrl}/api/workflows/${wfId}/execution-status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setNodes(data.nodes || []);
        setLogs(data.logs || []);
        setStatus(data.status || 'Pending');
        setExecutionId(data.execution_id || '');
      }
    } catch (err) {
      console.error(err);
    }
  };

  // Sync to active workflow if passed in from App
  useEffect(() => {
    if (activeWorkflow) {
      setSelectedWorkflowId(activeWorkflow.id);
    }
  }, [activeWorkflow]);

  // Load status and start polling if running
  useEffect(() => {
    if (!selectedWorkflowId) return;

    fetchStatus(selectedWorkflowId);

    const interval = setInterval(() => {
      fetchStatus(selectedWorkflowId);
    }, 1000);

    return () => clearInterval(interval);
  }, [selectedWorkflowId]);

  // Auto scroll logs console to bottom
  useEffect(() => {
    if (logTerminalRef.current) {
      logTerminalRef.current.scrollTop = logTerminalRef.current.scrollHeight;
    }
  }, [logs]);

  if (!selectedWorkflowId) {
    return (
      <GlassCard className="text-center py-16">
        <Activity className="w-12 h-12 text-violet-400 mx-auto mb-3 animate-pulse" />
        <h3 className="text-lg font-bold text-slate-700 dark:text-slate-200">No active execution monitor</h3>
        <p className="text-xs text-slate-400 max-w-sm mx-auto mt-2">
          Execute a workflow pipeline from the Workflow Builder to observe real-time agent delegation logs.
        </p>
      </GlassCard>
    );
  }

  return (
    <div className="space-y-6">
      {/* Overview Card */}
      <GlassCard glow={status === 'Running' ? 'violet' : 'none'}>
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div className="flex items-center gap-3">
            <div className={`p-2.5 rounded-xl border flex items-center justify-center ${
              status === 'Running' ? 'bg-violet-500/10 text-violet-500 border-violet-500/20' :
              status === 'Completed' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' :
              status === 'Failed' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
              'bg-slate-500/10 text-slate-500 border-slate-500/20'
            }`}>
              <Activity className={`w-5 h-5 ${status === 'Running' ? 'animate-spin' : ''}`} />
            </div>
            <div>
              <span className="text-[10px] text-slate-400 uppercase font-bold tracking-wider">Telemetry Link</span>
              <h3 className="text-md font-bold text-slate-800 dark:text-white flex items-center gap-2">
                Execution-ID: <span className="font-mono text-violet-500">{executionId || 'AURA_MOCK_REF'}</span>
              </h3>
            </div>
          </div>

          <div className="flex items-center gap-3">
            <span className={`text-[10px] font-bold px-2.5 py-1 rounded-full border uppercase ${
              status === 'Completed' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' :
              status === 'Failed' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
              status === 'Running' ? 'bg-violet-500/10 text-violet-500 border-violet-500/20' :
              'bg-slate-500/10 text-slate-500 border-slate-500/20'
            }`}>
              {status}
            </span>
          </div>
        </div>
      </GlassCard>

      {/* Main Console Splitter */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
        
        {/* Left pane: Pipeline Step Checklist Timeline */}
        <GlassCard className="lg:col-span-5 h-[450px] flex flex-col">
          <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 mb-4 flex items-center gap-2">
            <Clock className="w-4 h-4 text-slate-400" />
            Execution Timeline
          </h4>

          <div className="flex-1 overflow-y-auto space-y-4 pr-1 relative pl-4 border-l border-slate-200 dark:border-white/5 ml-3">
            {nodes.map((node) => {
              let StepIcon = Clock;
              let iconColor = 'text-slate-400 border-slate-300 dark:border-white/10 bg-slate-50 dark:bg-black/10';
              
              if (node.status === 'Completed') {
                StepIcon = CheckCircle;
                iconColor = 'text-emerald-500 border-emerald-500/30 bg-emerald-500/10';
              } else if (node.status === 'Failed') {
                StepIcon = AlertCircle;
                iconColor = 'text-red-500 border-red-500/30 bg-red-500/10';
              } else if (node.status === 'Running') {
                StepIcon = Loader;
                iconColor = 'text-violet-500 border-violet-500/30 bg-violet-500/10 animate-spin';
              }

              return (
                <div key={node.id} className="relative flex gap-4 text-xs select-none">
                  {/* Timeline indicator node */}
                  <div className={`absolute -left-[27px] w-6 h-6 rounded-full border flex items-center justify-center z-10 ${iconColor}`}>
                    <StepIcon className="w-3.5 h-3.5" />
                  </div>

                  <div className="flex-1 pb-1">
                    <div className="flex items-center justify-between">
                      <h5 className="font-bold text-slate-700 dark:text-slate-200">{node.label}</h5>
                      <span className="text-[9px] uppercase font-bold text-slate-400">{node.status}</span>
                    </div>
                    <p className="text-[10px] text-slate-400 mt-0.5">
                      Delegated to: {node.type.toUpperCase()} Agent
                    </p>
                  </div>
                </div>
              );
            })}
          </div>
        </GlassCard>

        {/* Right pane: Real-time Terminal Log Output */}
        <GlassCard className="lg:col-span-7 h-[450px] flex flex-col bg-[#080911] border-slate-900 overflow-hidden">
          <div className="flex items-center justify-between pb-3 border-b border-slate-800/80 mb-3">
            <h4 className="text-xs font-bold text-slate-400 flex items-center gap-1.5 font-mono">
              <Terminal className="w-4 h-4 text-violet-500" />
              stdout - agent_logs.txt
            </h4>
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 animate-pulse" />
          </div>

          {/* Terminal stream block */}
          <div 
            ref={logTerminalRef}
            className="flex-1 overflow-y-auto font-mono text-[11px] space-y-1.5 pr-2 text-slate-300 custom-terminal-scroll"
          >
            {logs.length === 0 ? (
              <div className="text-slate-500 text-center py-20 italic">
                Initializing communication socket... Waiting for agent payload.
              </div>
            ) : (
              logs.map((log, index) => {
                let lvlColor = 'text-slate-400';
                if (log.level === 'SUCCESS') lvlColor = 'text-emerald-400 font-bold';
                if (log.level === 'ERROR') lvlColor = 'text-red-400 font-bold';
                if (log.level === 'WARNING') lvlColor = 'text-amber-400 font-bold';
                
                return (
                  <div key={index} className="flex gap-2 leading-relaxed animate-in fade-in-25 duration-150">
                    <span className="text-slate-600">[{new Date(log.timestamp).toLocaleTimeString()}]</span>
                    <span className={`uppercase shrink-0 ${lvlColor}`}>[{log.level}]</span>
                    <span className="text-slate-500 font-bold shrink-0">{log.agent_name}:</span>
                    <span className="text-slate-200">{log.message}</span>
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
