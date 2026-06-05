from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Command, Workflow, WorkflowNode, Execution, ExecutionLog
from backend.app.security import get_current_user
from backend.app.schemas import WorkflowResponse, WorkflowNodeResponse, ExecutionResponse
from backend.app.nlp.agents_sim import AgentSimulator

router = APIRouter()

class WorkflowGenReq(BaseModel):
    command_id: str

@router.post("/generate", response_model=WorkflowResponse)
def generate_workflow(
    req: WorkflowGenReq,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uid = user["uid"]
    
    # 1. Fetch Command from SQL
    cmd = db.query(Command).filter(Command.id == req.command_id).first()
    if not cmd:
        raise HTTPException(status_code=404, detail="Command not found")
        
    title = f"Workflow: {cmd.intent.replace('_', ' ').title()}" if cmd.intent else "Workflow: Custom Task"
    
    # 2. Write Workflow Document
    wf = Workflow(
        user_id=uid,
        command_id=req.command_id,
        name=title,
        status="Pending",
        success_rate=0.0
    )
    db.add(wf)
    db.commit()
    db.refresh(wf)

    # 3. Write Workflow Nodes
    task_decomp = cmd.task_decomposition or []
    nodes_list = []
    
    for idx, task in enumerate(task_decomp):
        node_id = f"node-{idx+1}-{wf.id[:8]}"
        node = WorkflowNode(
            id=node_id,
            workflow_id=wf.id,
            label=task.get("label", ""),
            type=task.get("type", "planner"),
            status="Pending",
            inputs=task.get("inputs", {}),
            outputs=task.get("outputs", {}),
            sequence_order=idx
        )
        db.add(node)
        nodes_list.append(node)
        
    db.commit()

    return WorkflowResponse(
        id=wf.id,
        command_id=req.command_id,
        name=title,
        status="Pending",
        success_rate=0.0,
        created_at=wf.created_at,
        nodes=[WorkflowNodeResponse(
            id=n.id,
            workflow_id=n.workflow_id,
            label=n.label,
            type=n.type,
            status=n.status,
            inputs=n.inputs or {},
            outputs=n.outputs or {},
            sequence_order=n.sequence_order
        ) for n in nodes_list]
    )

@router.get("/{id}", response_model=WorkflowResponse)
def get_workflow(
    id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    wf = db.query(Workflow).filter(Workflow.id == id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    # Fetch nodes
    nodes = db.query(WorkflowNode).filter(WorkflowNode.workflow_id == id).order_by(WorkflowNode.sequence_order).all()
        
    return WorkflowResponse(
        id=wf.id,
        command_id=wf.command_id,
        name=wf.name,
        status=wf.status,
        success_rate=wf.success_rate,
        created_at=wf.created_at,
        nodes=[WorkflowNodeResponse(
            id=n.id,
            workflow_id=n.workflow_id,
            label=n.label,
            type=n.type,
            status=n.status,
            inputs=n.inputs or {},
            outputs=n.outputs or {},
            sequence_order=n.sequence_order
        ) for n in nodes]
    )

@router.post("/{id}/execute", response_model=ExecutionResponse)
def execute_workflow(
    id: str,
    background_tasks: BackgroundTasks,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uid = user["uid"]
    
    wf = db.query(Workflow).filter(Workflow.id == id).first()
    if not wf:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    # Reset all node statuses to pending
    nodes = db.query(WorkflowNode).filter(WorkflowNode.workflow_id == id).all()
    for node in nodes:
        node.status = "Pending"
        
    wf.status = "Running"

    # Create new Execution document
    new_exec = Execution(
        user_id=uid,
        workflow_id=id,
        status="Running"
    )
    db.add(new_exec)
    db.commit()
    db.refresh(new_exec)

    # Spawn simulator task
    simulator = AgentSimulator()
    background_tasks.add_task(simulator.execute_workflow_sql, new_exec.id, id)

    return ExecutionResponse(
        id=new_exec.id,
        workflow_id=id,
        status="Running",
        started_at=new_exec.started_at
    )

@router.get("/{id}/execution-status")
def get_execution_status(
    id: str,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uid = user["uid"]
    
    # Get latest execution for this workflow
    latest_exec = db.query(Execution)\
        .filter(Execution.workflow_id == id, Execution.user_id == uid)\
        .order_by(Execution.started_at.desc())\
        .first()
        
    if not latest_exec:
        return {"status": "Pending", "logs": [], "nodes": []}
        
    # Fetch nodes
    nodes = db.query(WorkflowNode).filter(WorkflowNode.workflow_id == id).order_by(WorkflowNode.sequence_order).all()
    
    # Fetch logs
    logs_list = db.query(ExecutionLog).filter(ExecutionLog.execution_id == latest_exec.id).order_by(ExecutionLog.timestamp.asc()).all()
    logs = [{
        "agent_name": l.agent_name,
        "level": l.level,
        "message": l.message,
        "timestamp": l.timestamp.isoformat() if hasattr(l.timestamp, 'isoformat') else str(l.timestamp)
    } for l in logs_list]

    return {
        "execution_id": latest_exec.id,
        "status": latest_exec.status,
        "started_at": latest_exec.started_at,
        "completed_at": latest_exec.completed_at,
        "nodes": [{
            "id": n.id,
            "workflow_id": n.workflow_id,
            "label": n.label,
            "type": n.type,
            "status": n.status,
            "inputs": n.inputs or {},
            "outputs": n.outputs or {},
            "sequence_order": n.sequence_order
        } for n in nodes],
        "logs": logs
    }

