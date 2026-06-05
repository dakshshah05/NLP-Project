from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Memory
from backend.app.security import get_current_user
from backend.app.schemas import MemoryCreate, MemoryResponse
from backend.app.nlp.vector_db import vector_db

router = APIRouter()

@router.get("/search")
def search_memory(query: str, category: Optional[str] = None, user: dict = Depends(get_current_user)):
    if not query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty")
    results = vector_db.search(query, category)
    return results

@router.post("/add", response_model=MemoryResponse)
def add_memory(
    payload: MemoryCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uid = user["uid"]
    
    if payload.category not in ["contacts", "commands", "preferences", "documents"]:
        raise HTTPException(status_code=400, detail="Invalid memory category")
    
    # 1. Add to the local vector simulator search list
    simulated_item = vector_db.add_item(payload.category, payload.content)

    # 2. Write to SQL
    new_mem = Memory(
        user_id=uid,
        category=payload.category,
        content=payload.content
    )
    db.add(new_mem)
    db.commit()
    db.refresh(new_mem)

    return new_mem

@router.get("/list", response_model=List[MemoryResponse])
def list_memories(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uid = user["uid"]
    
    # Fetch from SQL
    sql_memories = db.query(Memory).filter(Memory.user_id == uid).all()
    
    memories = []
    for m in sql_memories:
        memories.append(MemoryResponse(
            id=m.id,
            category=m.category,
            content=m.content,
            created_at=m.created_at
        ))
        
    # Append default seeded items from the simulator
    for sim in vector_db.memories:
        sim_id = sim["id"]
        # Verify no duplicate id
        if not any(item.id == sim_id for item in memories):
            memories.append(MemoryResponse(
                id=sim_id,
                category=sim["category"],
                content=sim["content"],
                created_at=datetime.utcnow()
            ))

    return memories

