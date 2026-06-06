import React, { useEffect, useState } from 'react';
import { GlassCard } from '../components/GlassCard';
import { NodeFlow } from '../components/NodeFlow';
import type { Command, Workflow, WorkflowNode } from '../types';
import { 
  GitFork, 
  Play, 
  Settings, 
  HelpCircle, 
  ArrowRight,
  Loader,
  CheckCircle,
  AlertCircle
} from 'lucide-react';

import { useAuth } from '../context/AuthContext';

interface WorkflowBuilderProps {
  selectedCommand: Command | null;
  activeWorkflow: Workflow | null;
  setActiveWorkflow: (workflow: Workflow) => void;
  setActiveTab: (tab: string) => void;
}

export const WorkflowBuilder: React.FC<WorkflowBuilderProps> = ({
  selectedCommand,
  activeWorkflow,
  setActiveWorkflow,
  setActiveTab
}) => {
  const { token } = useAuth();
  const [generating, setGenerating] = useState(false);
  const [running, setRunning] = useState(false);
  const [nodes, setNodes] = useState<WorkflowNode[]>([]);
  const [executionStatus, setExecutionStatus] = useState<string>('Pending');

  // Load workflow nodes if a workflow is active
  const fetchWorkflowDetails = async (workflowId: string) => {
    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${backendUrl}/api/workflows/${workflowId}/execution-status`, {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        const data = await res.json();
        setNodes(data.nodes || []);
        setExecutionStatus(data.status || 'Pending');
        
        // Update global state
        if (activeWorkflow) {
          setActiveWorkflow({
            ...activeWorkflow,
            status: data.status
          });
        }
      }
    } catch (err) {
      console.error('Error fetching execution details', err);
    }
  };

  useEffect(() => {
    if (activeWorkflow && token) {
      fetchWorkflowDetails(activeWorkflow.id);
    } else {
      setNodes([]);
      setExecutionStatus('Pending');
    }
  }, [activeWorkflow, token]);

  // Poll for status updates if running
  useEffect(() => {
    let interval: any;
    if (activeWorkflow && token && (executionStatus === 'Running' || executionStatus === 'Pending' || running)) {
      interval = setInterval(() => {
        fetchWorkflowDetails(activeWorkflow.id);
      }, 1000);
    }
    return () => {
      if (interval) clearInterval(interval);
    };
  }, [activeWorkflow, executionStatus, running, token]);

  // Stop spinning loader if execution completes or fails
  useEffect(() => {
    if (executionStatus === 'Completed' || executionStatus === 'Failed') {
      setRunning(false);
    }
  }, [executionStatus]);

  const handleGenerateWorkflow = async () => {
    if (!selectedCommand) return;
    setGenerating(true);

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${backendUrl}/api/workflows/generate`, {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`
        },
        body: JSON.stringify({ command_id: selectedCommand.id }),
      });

      if (res.ok) {
        const workflowData: Workflow = await res.json();
        setActiveWorkflow(workflowData);
      }
    } catch (err) {
      console.error('Failed to generate workflow', err);
    } finally {
      setGenerating(false);
    }
  };

  const handleRunExecution = async () => {
    if (!activeWorkflow) return;
    setRunning(true);

    try {
      const backendUrl = import.meta.env.VITE_BACKEND_URL || 'http://127.0.0.1:8000';
      const res = await fetch(`${backendUrl}/api/workflows/${activeWorkflow.id}/execute`, {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });
      if (res.ok) {
        // Trigger page refresh loop
        fetchWorkflowDetails(activeWorkflow.id);
      }
    } catch (err) {
      console.error('Failed to start execution', err);
      setRunning(false);
    }
  };

  return (
    <div className="space-y-6">
      {!activeWorkflow ? (
        // Mode 1: No workflow generated yet
        <GlassCard className="text-center py-16">
          <GitFork className="w-12 h-12 text-violet-400 mx-auto mb-3 animate-bounce" />
          <h3 className="text-lg font-bold text-slate-700 dark:text-slate-200">
            {selectedCommand ? 'Workflow Blueprint Ready' : 'No Active Directive'}
          </h3>
          <p className="text-xs text-slate-400 max-w-sm mx-auto mt-2 mb-6">
            {selectedCommand 
              ? 'AURA has decomposed this command into a multi-step execution. Compile the nodes to generate the workflow.'
              : 'Execute a natural language command in the Command Center first to design a workflow.'}
          </p>

          {selectedCommand && (
            <button
              onClick={handleGenerateWorkflow}
              disabled={generating}
              className="px-6 py-3 rounded-xl bg-violet-600 hover:bg-violet-700 text-white font-semibold text-xs shadow-lg shadow-violet-500/20 transition-all flex items-center gap-2 mx-auto disabled:opacity-50"
            >
              {generating ? (
                <>
                  <Loader className="w-4 h-4 animate-spin" />
                  Generating DAG...
                </>
              ) : (
                <>
                  <Settings className="w-4 h-4 animate-spin" style={{ animationDuration: '4s' }} />
                  Generate Agent Workflow
                </>
              )}
            </button>
          )}
        </GlassCard>
      ) : (
        // Mode 2: Workflow is generated, display nodes, visualization, & run controls
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-6">
          
          {/* Node Visualization Chart */}
          <div className="lg:col-span-8 space-y-6">
            <GlassCard className="flex flex-col">
              <div className="flex items-center justify-between mb-4">
                <div>
                  <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200">
                    Interactive Pipeline Canvas
                  </h4>
                  <span className="text-[10px] text-slate-400 font-semibold block mt-0.5">
                    Drag nodes to adjust layouts. Arrows indicate order of agent delegation.
                  </span>
                </div>

                <div className="flex items-center gap-3">
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded border uppercase flex items-center gap-1.5 ${
                    executionStatus === 'Completed' ? 'bg-emerald-500/10 text-emerald-500 border-emerald-500/20' :
                    executionStatus === 'Failed' ? 'bg-red-500/10 text-red-500 border-red-500/20' :
                    executionStatus === 'Running' ? 'bg-violet-500/10 text-violet-500 border-violet-500/20' :
                    'bg-slate-500/10 text-slate-500 border-slate-500/20'
                  }`}>
                    {executionStatus === 'Running' && <Loader className="w-3 h-3 animate-spin" />}
                    {executionStatus}
                  </span>

                  <button
                    onClick={handleRunExecution}
                    disabled={running || executionStatus === 'Running'}
                    className="px-4 py-2 rounded-xl bg-emerald-600 hover:bg-emerald-700 text-white font-semibold text-xs transition-all flex items-center gap-1.5 shadow-md shadow-emerald-500/10 disabled:opacity-50"
                  >
                    <Play className="w-3.5 h-3.5" />
                    Run Pipeline
                  </button>
                </div>
              </div>

              {/* Node Flow chart */}
              <NodeFlow nodesList={nodes} workflowStatus={executionStatus} />
            </GlassCard>
          </div>

          {/* Workflow details & metrics panel */}
          <div className="lg:col-span-4 space-y-6">
            <GlassCard className="h-full flex flex-col justify-between">
              <div>
                <h4 className="text-sm font-bold text-slate-800 dark:text-slate-200 border-b border-slate-100 dark:border-white/5 pb-3 mb-4">
                  Pipeline Details
                </h4>

                <div className="space-y-4 text-xs">
                  <div>
                    <span className="text-slate-400 font-semibold uppercase text-[10px] block">Workflow Name</span>
                    <span className="font-bold text-slate-700 dark:text-slate-200 mt-1 block">{activeWorkflow.name}</span>
                  </div>
                  
                  <div>
                    <span className="text-slate-400 font-semibold uppercase text-[10px] block">Steps Count</span>
                    <span className="font-bold text-slate-700 dark:text-slate-200 mt-1 block">{nodes.length} Actions</span>
                  </div>

                  <div>
                    <span className="text-slate-400 font-semibold uppercase text-[10px] block">Success Probability</span>
                    <span className="font-bold text-violet-500 mt-1 block">
                      {activeWorkflow.success_rate > 0 ? `${activeWorkflow.success_rate}%` : '98.2%'}
                    </span>
                  </div>

                  <div>
                    <span className="text-slate-400 font-semibold uppercase text-[10px] block">Sequence Map</span>
                    <div className="mt-2 space-y-2">
                      {nodes.map((node) => {
                        let statusColor = 'text-slate-400';
                        let StatusIcon = HelpCircle;
                        if (node.status === 'Completed') {
                          statusColor = 'text-emerald-500';
                          StatusIcon = CheckCircle;
                        } else if (node.status === 'Failed') {
                          statusColor = 'text-red-500';
                          StatusIcon = AlertCircle;
                        } else if (node.status === 'Running') {
                          statusColor = 'text-violet-500';
                          StatusIcon = Loader;
                        }

                        return (
                          <div key={node.id} className="flex items-center justify-between p-2 rounded-xl bg-slate-100/10 dark:bg-white/5 border border-slate-200/20">
                            <span className="font-medium text-slate-600 dark:text-slate-300 truncate max-w-[150px]">{node.label}</span>
                            <StatusIcon className={`w-4 h-4 ${statusColor} ${node.status === 'Running' ? 'animate-spin' : ''}`} />
                          </div>
                        );
                      })}
                    </div>
                  </div>
                </div>
              </div>

              {executionStatus === 'Running' && (
                <button
                  onClick={() => setActiveTab('execution-monitor')}
                  className="mt-6 w-full py-2.5 rounded-xl border border-violet-500/20 bg-violet-500/10 hover:bg-violet-500/20 text-violet-500 font-semibold text-xs flex items-center justify-center gap-1.5 transition-all"
                >
                  Open Live Monitor <ArrowRight className="w-4 h-4" />
                </button>
              )}
            </GlassCard>
          </div>
        </div>
      )}
    </div>
  );
};
