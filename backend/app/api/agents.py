from fastapi import APIRouter, Depends, HTTPException
from typing import List
from backend.app.firebase_config import db_firestore
from backend.app.security import get_current_user
from backend.app.schemas import AgentResponse, AgentToggle
from backend.app.nlp.agents_sim import AGENT_CAPABILITIES

router = APIRouter()

def seed_agents_firestore():
    for name, capabilities in AGENT_CAPABILITIES.items():
        db_firestore.collection("agents").document(name).set({
            "name": name,
            "status": "Idle",
            "tasks_completed": 0,
            "success_rate": 100.0,
            "capabilities": capabilities
        })

@router.get("", response_model=List[AgentResponse])
def get_agents(user: dict = Depends(get_current_user)):
    agents_ref = db_firestore.collection("agents")
    docs = agents_ref.get()
    
    if len(docs) == 0:
        seed_agents_firestore()
        docs = agents_ref.get()

    agents = []
    for doc in docs:
        data = doc.to_dict()
        agents.append(AgentResponse(
            name=data.get("name", ""),
            status=data.get("status", "Idle"),
            tasks_completed=data.get("tasks_completed", 0),
            success_rate=data.get("success_rate", 100.0),
            capabilities=data.get("capabilities", [])
        ))
    return agents

@router.post("/{name}/toggle", response_model=AgentResponse)
def toggle_agent(name: str, payload: AgentToggle, user: dict = Depends(get_current_user)):
    agent_ref = db_firestore.collection("agents").document(name)
    agent_doc = agent_ref.get()
    
    if not agent_doc.exists:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if payload.status not in ["Idle", "Active", "Disabled"]:
        raise HTTPException(status_code=400, detail="Invalid agent status")

    agent_ref.update({"status": payload.status})
    
    # Return updated agent details
    data = agent_ref.get().to_dict()
    return AgentResponse(
        name=data.get("name", ""),
        status=data.get("status", "Idle"),
        tasks_completed=data.get("tasks_completed", 0),
        success_rate=data.get("success_rate", 100.0),
        capabilities=data.get("capabilities", [])
    )
