from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
from backend.app.firebase_config import db_firestore
from backend.app.security import get_current_user
from backend.app.schemas import WorkflowResponse, WorkflowNodeResponse, ExecutionResponse
from backend.app.nlp.agents_sim import AgentSimulator

router = APIRouter()

class WorkflowGenReq(BaseModel):
    command_id: str

@router.post("/generate", response_model=WorkflowResponse)
def generate_workflow(req: WorkflowGenReq, user: dict = Depends(get_current_user)):
    uid = user["uid"]
    
    # 1. Fetch Command from Firestore
    cmd_ref = db_firestore.collection("commands").document(req.command_id)
    cmd_doc = cmd_ref.get()
    
    if not cmd_doc.exists:
        raise HTTPException(status_code=404, detail="Command not found")
        
    cmd_data = cmd_doc.to_dict()
    title = f"Workflow: {cmd_data.get('intent', 'Task').replace('_', ' ').title()}"
    
    # 2. Write Workflow Document
    wf_ref = db_firestore.collection("workflows").document()
    wf_data = {
        "userId": uid,
        "commandId": req.command_id,
        "name": title,
        "status": "Pending",
        "success_rate": 0.0,
        "created_at": datetime.utcnow().isoformat()
    }
    wf_ref.set(wf_data)

    # 3. Write Workflow Nodes
    task_decomp = cmd_data.get("task_decomposition", [])
    nodes_list = []
    
    for idx, task in enumerate(task_decomp):
        node_id = f"node-{idx+1}"
        node_data = {
            "id": node_id,
            "workflow_id": wf_ref.id,
            "label": task.get("label", ""),
            "type": task.get("type", "planner"),
            "status": "Pending",
            "inputs": task.get("inputs", {}),
            "outputs": task.get("outputs", {}),
            "sequence_order": idx
        }
        wf_ref.collection("nodes").document(node_id).set(node_data)
        nodes_list.append(WorkflowNodeResponse(**node_data))

    return WorkflowResponse(
        id=wf_ref.id,
        command_id=req.command_id,
        name=title,
        status="Pending",
        success_rate=0.0,
        created_at=datetime.fromisoformat(wf_data["created_at"]),
        nodes=nodes_list
    )

@router.get("/{id}", response_model=WorkflowResponse)
def get_workflow(id: str, user: dict = Depends(get_current_user)):
    wf_ref = db_firestore.collection("workflows").document(id)
    wf_doc = wf_ref.get()
    
    if not wf_doc.exists:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    data = wf_doc.to_dict()
    
    # Fetch nodes
    nodes_docs = wf_ref.collection("nodes").order_by("sequence_order").get()
    nodes = []
    for doc in nodes_docs:
        nodes.append(WorkflowNodeResponse(**doc.to_dict()))
        
    return WorkflowResponse(
        id=wf_ref.id,
        command_id=data.get("commandId"),
        name=data.get("name", ""),
        status=data.get("status", "Pending"),
        success_rate=data.get("success_rate", 0.0),
        created_at=datetime.fromisoformat(data["created_at"]) if isinstance(data.get("created_at"), str) else datetime.utcnow(),
        nodes=nodes
    )

@router.post("/{id}/execute", response_model=ExecutionResponse)
def execute_workflow(id: str, background_tasks: BackgroundTasks, user: dict = Depends(get_current_user)):
    uid = user["uid"]
    
    wf_ref = db_firestore.collection("workflows").document(id)
    wf_doc = wf_ref.get()
    if not wf_doc.exists:
        raise HTTPException(status_code=404, detail="Workflow not found")
        
    # Reset all node statuses to pending
    nodes_docs = wf_ref.collection("nodes").get()
    for doc in nodes_docs:
        doc.reference.update({"status": "Pending"})
        
    wf_ref.update({"status": "Running"})

    # Create new Execution document
    exec_ref = db_firestore.collection("executions").document()
    exec_data = {
        "userId": uid,
        "workflowId": id,
        "status": "Running",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "logs": []
    }
    exec_ref.set(exec_data)

    # Spawn simulator task
    simulator = AgentSimulator()
    background_tasks.add_task(simulator.execute_workflow_firestore, exec_ref.id, id)

    return ExecutionResponse(
        id=exec_ref.id,
        workflow_id=id,
        status="Running",
        started_at=datetime.fromisoformat(exec_data["started_at"])
    )

@router.get("/{id}/execution-status")
def get_execution_status(id: str, user: dict = Depends(get_current_user)):
    uid = user["uid"]
    
    # Get latest execution for this workflow
    execs_ref = db_firestore.collection("executions")\
        .where("workflowId", "==", id)\
        .where("userId", "==", uid)
        
    execs_docs = execs_ref.get()
    if not execs_docs:
        return {"status": "Pending", "logs": [], "nodes": []}
        
    # Sort locally by started_at descending
    sorted_execs = sorted(execs_docs, key=lambda x: x.to_dict().get("started_at", ""), reverse=True)
    latest_exec = sorted_execs[0]
    exec_data = latest_exec.to_dict()
    
    # Fetch nodes
    wf_ref = db_firestore.collection("workflows").document(id)
    nodes_docs = wf_ref.collection("nodes").order_by("sequence_order").get()
    
    nodes = [doc.to_dict() for doc in nodes_docs]
    logs = exec_data.get("logs", [])

    return {
        "execution_id": latest_exec.id,
        "status": exec_data.get("status"),
        "started_at": exec_data.get("started_at"),
        "completed_at": exec_data.get("completed_at"),
        "nodes": nodes,
        "logs": logs
    }
