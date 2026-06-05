from fastapi import APIRouter, Depends, HTTPException
from typing import List
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Agent
from backend.app.security import get_current_user
from backend.app.schemas import AgentResponse, AgentToggle
from backend.app.nlp.agents_sim import AGENT_CAPABILITIES

router = APIRouter()

def seed_agents_sql(db: Session):
    for name, capabilities in AGENT_CAPABILITIES.items():
        # Check if already exists to avoid conflict
        existing = db.query(Agent).filter(Agent.name == name).first()
        if not existing:
            new_agent = Agent(
                name=name,
                status="Idle",
                tasks_completed=0,
                success_rate=100.0,
                capabilities=capabilities
            )
            db.add(new_agent)
    db.commit()

@router.get("", response_model=List[AgentResponse])
def get_agents(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agents_list = db.query(Agent).all()
    
    if len(agents_list) == 0:
        seed_agents_sql(db)
        agents_list = db.query(Agent).all()

    return agents_list

@router.post("/{name}/toggle", response_model=AgentResponse)
def toggle_agent(
    name: str,
    payload: AgentToggle,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    agent = db.query(Agent).filter(Agent.name == name).first()
    
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    if payload.status not in ["Idle", "Active", "Disabled"]:
        raise HTTPException(status_code=400, detail="Invalid agent status")

    agent.status = payload.status
    db.commit()
    db.refresh(agent)
    
    return agent

