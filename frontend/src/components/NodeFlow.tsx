import React, { useMemo } from 'react';
import ReactFlow, { 
  Background, 
  Controls, 
  MarkerType,
  type Node,
  type Edge
} from 'reactflow';
import 'reactflow/dist/style.css';
import type { WorkflowNode } from '../types';

interface NodeFlowProps {
  nodesList: WorkflowNode[];
  workflowStatus?: string;
}

export const NodeFlow: React.FC<NodeFlowProps> = ({ nodesList }) => {
  
  // Transform DB Workflow Nodes into React Flow nodes and edges
  const { nodes, edges } = useMemo(() => {
    if (!nodesList || nodesList.length === 0) {
      // Default placeholder pipeline structure
      const defaultLabels = [
        { id: '1', label: 'Natural Language Input', type: 'input' },
        { id: '2', label: 'Intent Detection', type: 'nlp' },
        { id: '3', label: 'Entity Extraction', type: 'nlp' },
        { id: '4', label: 'Task Decomposition', type: 'planner' },
        { id: '5', label: 'Workflow Generation', type: 'planner' },
        { id: '6', label: 'Execution', type: 'execution' }
      ];

      const flowNodes: Node[] = defaultLabels.map((item, idx) => ({
        id: item.id,
        position: { x: 250, y: idx * 100 },
        data: { label: item.label },
        style: {
          background: 'rgba(139, 92, 246, 0.1)',
          color: '#8b5cf6',
          border: '1px solid rgba(139, 92, 246, 0.3)',
          borderRadius: '12px',
          padding: '10px',
          fontWeight: 600,
          fontSize: '12px',
          width: 200,
          textAlign: 'center',
          backdropFilter: 'blur(8px)'
        }
      }));

      const flowEdges: Edge[] = [];
      for (let i = 0; i < defaultLabels.length - 1; i++) {
        flowEdges.push({
          id: `e${i+1}-${i+2}`,
          source: (i + 1).toString(),
          target: (i + 2).toString(),
          animated: true,
          style: { stroke: '#8b5cf6' },
          markerEnd: { type: MarkerType.ArrowClosed, color: '#8b5cf6' }
        });
      }

      return { nodes: flowNodes, edges: flowEdges };
    }

    // Build from real nodes
    const flowNodes: Node[] = nodesList.map((node, idx) => {
      // Style node based on status
      let bg = 'rgba(255, 255, 255, 0.5)';
      let border = '1px solid rgba(255, 255, 255, 0.15)';
      let text = '#475569';
      let shadow = 'none';

      if (node.status === 'Running') {
        bg = 'rgba(139, 92, 246, 0.15)';
        border = '1.5px solid #8b5cf6';
        text = '#8b5cf6';
        shadow = '0 0 15px rgba(139, 92, 246, 0.2)';
      } else if (node.status === 'Completed') {
        bg = 'rgba(16, 185, 129, 0.15)';
        border = '1.5px solid #10b981';
        text = '#10b981';
      } else if (node.status === 'Failed') {
        bg = 'rgba(239, 68, 68, 0.15)';
        border = '1.5px solid #ef4444';
        text = '#ef4444';
      }

      return {
        id: node.id,
        position: { x: 250, y: idx * 100 },
        data: { 
          label: (
            <div className="flex flex-col items-center">
              <span className="font-semibold text-xs text-slate-800 dark:text-slate-200">
                {node.label}
              </span>
              <span className="text-[9px] uppercase font-bold tracking-wider mt-1 opacity-80">
                Agent: {node.type} | {node.status}
              </span>
            </div>
          )
        },
        style: {
          background: bg,
          border: border,
          borderRadius: '16px',
          padding: '12px 8px',
          color: text,
          width: 220,
          boxShadow: shadow,
          backdropFilter: 'blur(12px)',
          transition: 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)'
        }
      };
    });

    const flowEdges: Edge[] = [];
    for (let i = 0; i < nodesList.length - 1; i++) {
      const sourceNode = nodesList[i];
      const targetNode = nodesList[i + 1];
      const isAnimated = sourceNode.status === 'Completed' && targetNode.status === 'Running';
      
      let edgeColor = '#cbd5e1'; // slate-300
      if (sourceNode.status === 'Completed') {
        edgeColor = '#10b981'; // emerald-500
      }
      if (targetNode.status === 'Failed') {
        edgeColor = '#ef4444'; // red-500
      }

      flowEdges.push({
        id: `e-${sourceNode.id}-${targetNode.id}`,
        source: sourceNode.id,
        target: targetNode.id,
        animated: isAnimated || sourceNode.status === 'Running',
        style: { stroke: edgeColor, strokeWidth: 2 },
        markerEnd: { 
          type: MarkerType.ArrowClosed, 
          color: edgeColor 
        }
      });
    }

    return { nodes: flowNodes, edges: flowEdges };
  }, [nodesList]);

  return (
    <div className="w-full h-[500px] border border-slate-200/50 dark:border-white/5 rounded-2xl bg-slate-50/50 dark:bg-black/15 overflow-hidden">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        fitView
        fitViewOptions={{ padding: 0.2 }}
        nodesConnectable={false}
        nodesDraggable={true}
        elementsSelectable={false}
      >
        <Background gap={16} size={1} color="#94a3b8" className="opacity-25" />
        <Controls showInteractive={false} position="bottom-right" />
      </ReactFlow>
    </div>
  );
};
