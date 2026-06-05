from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from datetime import datetime

# Command schemas
class CommandCreate(BaseModel):
    text: str

class CommandResponse(BaseModel):
    id: str
    original_text: str
    language: str
    intent: Optional[str]
    intent_confidence: float
    entities: Dict[str, Any]
    semantic_parse: Dict[str, Any]
    context_resolution: Dict[str, Any]
    task_decomposition: List[Dict[str, Any]]
    created_at: datetime

    class Config:
        from_attributes = True

# Workflow schemas
class WorkflowNodeResponse(BaseModel):
    id: str
    workflow_id: str
    label: str
    type: str
    status: str
    inputs: Dict[str, Any]
    outputs: Dict[str, Any]
    sequence_order: int

    class Config:
        from_attributes = True

class WorkflowResponse(BaseModel):
    id: str
    command_id: Optional[str]
    name: str
    status: str
    success_rate: float
    created_at: datetime
    nodes: List[WorkflowNodeResponse] = []

    class Config:
        from_attributes = True

# Execution schemas
class ExecutionResponse(BaseModel):
    id: str
    workflow_id: str
    status: str
    started_at: datetime
    completed_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class ExecutionLogResponse(BaseModel):
    id: str
    execution_id: str
    agent_name: str
    level: str
    message: str
    timestamp: datetime

    class Config:
        from_attributes = True

# Agent schemas
class AgentResponse(BaseModel):
    name: str
    status: str
    tasks_completed: int
    success_rate: float
    capabilities: List[str]

    class Config:
        from_attributes = True

class AgentToggle(BaseModel):
    status: str

# Memory schemas
class MemoryCreate(BaseModel):
    category: str
    content: str

class MemoryResponse(BaseModel):
    id: str
    category: str
    content: str
    created_at: datetime

    class Config:
        from_attributes = True

# Dashboard schemas
class RecentActivity(BaseModel):
    id: str
    type: str # command, execution, alert
    description: str
    timestamp: datetime

class DashboardStats(BaseModel):
    total_commands: int
    tasks_completed: int
    active_agents: int
    success_rate: float
    recent_activities: List[RecentActivity]
    workflow_stats: Dict[str, Any]
