export interface Command {
  id: string;
  original_text: string;
  language: string;
  intent: string;
  intent_confidence: number;
  entities: {
    recipient?: string | null;
    subject?: string | null;
    filename?: string | null;
    url?: string | null;
    date_time?: string | null;
    keywords?: string[];
    [key: string]: any;
  };
  semantic_parse: {
    semantic_relations: {
      action: string;
      actor: string;
      object: string;
      instrument: string;
    };
    dependency_tree_status: string;
    logical_form: string;
  };
  context_resolution: {
    active_session: string;
    resolved_references: {
      it: string;
      them: string;
    };
    user_preferences: {
      language_preference: string;
      preferred_agent: string;
    };
  };
  task_decomposition: {
    id: string;
    label: string;
    type: string;
    inputs: Record<string, any>;
    outputs: Record<string, any>;
  }[];
  created_at: string;
}

export interface WorkflowNode {
  id: string;
  workflow_id: string;
  label: string;
  type: string;
  status: 'Pending' | 'Running' | 'Completed' | 'Failed';
  inputs: Record<string, any>;
  outputs: Record<string, any>;
  sequence_order: number;
}

export interface Workflow {
  id: string;
  command_id: string | null;
  name: string;
  status: 'Pending' | 'Running' | 'Completed' | 'Failed';
  success_rate: number;
  created_at: string;
  nodes?: WorkflowNode[];
}

export interface ExecutionLog {
  agent_name: string;
  level: 'INFO' | 'WARNING' | 'ERROR' | 'SUCCESS';
  message: string;
  timestamp: string;
}

export interface Agent {
  name: string;
  status: 'Idle' | 'Active' | 'Disabled';
  tasks_completed: number;
  success_rate: number;
  capabilities: string[];
}

export interface Memory {
  id: string;
  category: 'contacts' | 'commands' | 'preferences' | 'documents';
  content: string;
  created_at: string;
  score?: number; // similarity score for search results
}

export interface RecentActivity {
  id: string;
  type: 'command' | 'execution' | 'alert';
  description: string;
  timestamp: string;
}

export interface DashboardStats {
  total_commands: number;
  tasks_completed: number;
  active_agents: number;
  success_rate: number;
  recent_activities: RecentActivity[];
  workflow_stats: {
    pending: number;
    running: number;
    completed: number;
    failed: number;
  };
}
