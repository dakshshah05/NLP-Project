import uuid
from sqlalchemy import Column, String, Float, DateTime, Integer, JSON, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
from backend.app.database import Base

# Helper function to generate string UUIDs for generic DB support (SQLite & Postgres)
def generate_uuid():
    return str(uuid.uuid4())

class Command(Base):
    __tablename__ = "commands"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(100), nullable=False, index=True)
    original_text = Column(Text, nullable=False)
    language = Column(String(50), default="English")
    intent = Column(String(100), nullable=True)
    intent_confidence = Column(Float, default=1.0)
    entities = Column(JSON, default={})
    semantic_parse = Column(JSON, default={})
    context_resolution = Column(JSON, default={})
    task_decomposition = Column(JSON, default=[])
    created_at = Column(DateTime, default=datetime.utcnow)

class Workflow(Base):
    __tablename__ = "workflows"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(100), nullable=False, index=True)
    command_id = Column(String(36), ForeignKey("commands.id"), nullable=True)
    name = Column(String(200), nullable=False)
    status = Column(String(50), default="Pending") # Pending, Running, Completed, Failed
    success_rate = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)

class WorkflowNode(Base):
    __tablename__ = "workflow_nodes"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    label = Column(String(200), nullable=False)
    type = Column(String(100), nullable=False) # email, document, file, browser, planner, memory
    status = Column(String(50), default="Pending") # Pending, Running, Completed, Failed
    inputs = Column(JSON, default={})
    outputs = Column(JSON, default={})
    sequence_order = Column(Integer, default=0)

class Execution(Base):
    __tablename__ = "executions"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(100), nullable=False, index=True)
    workflow_id = Column(String(36), ForeignKey("workflows.id"), nullable=False)
    status = Column(String(50), default="Pending")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

class ExecutionLog(Base):
    __tablename__ = "execution_logs"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    execution_id = Column(String(36), ForeignKey("executions.id"), nullable=False)
    agent_name = Column(String(100), nullable=False)
    level = Column(String(50), default="INFO") # INFO, WARNING, ERROR, SUCCESS
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)

class Agent(Base):
    __tablename__ = "agents"

    name = Column(String(100), primary_key=True) # e.g. Planner Agent, Email Agent, etc.
    status = Column(String(50), default="Idle") # Idle, Active, Disabled
    tasks_completed = Column(Integer, default=0)
    success_rate = Column(Float, default=100.0)
    capabilities = Column(JSON, default=[])

class Memory(Base):
    __tablename__ = "memories"

    id = Column(String(36), primary_key=True, default=generate_uuid)
    user_id = Column(String(100), nullable=False, index=True)
    category = Column(String(100), nullable=False) # contacts, commands, preferences, documents
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
