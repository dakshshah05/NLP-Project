from fastapi import APIRouter, Depends, HTTPException
from typing import List, Optional
from datetime import datetime
from backend.app.firebase_config import db_firestore
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
def add_memory(payload: MemoryCreate, user: dict = Depends(get_current_user)):
    uid = user["uid"]
    
    if payload.category not in ["contacts", "commands", "preferences", "documents"]:
        raise HTTPException(status_code=400, detail="Invalid memory category")
    
    # 1. Add to the local vector simulator search list
    simulated_item = vector_db.add_item(payload.category, payload.content)

    # 2. Write to Firestore
    mem_ref = db_firestore.collection("memories").document()
    mem_data = {
        "userId": uid,
        "category": payload.category,
        "content": payload.content,
        "created_at": datetime.utcnow().isoformat()
    }
    mem_ref.set(mem_data)

    return MemoryResponse(
        id=mem_ref.id,
        category=mem_data["category"],
        content=mem_data["content"],
        created_at=datetime.fromisoformat(mem_data["created_at"])
    )

@router.get("/list", response_model=List[MemoryResponse])
def list_memories(user: dict = Depends(get_current_user)):
    uid = user["uid"]
    
    # Fetch from Firestore
    memories_ref = db_firestore.collection("memories").where("userId", "==", uid)
    docs = memories_ref.get()

    memories = []
    for doc in docs:
        data = doc.to_dict()
        created_at_val = data.get("created_at")
        timestamp = datetime.fromisoformat(created_at_val) if isinstance(created_at_val, str) else datetime.utcnow()
        memories.append(MemoryResponse(
            id=doc.id,
            category=data.get("category", ""),
            content=data.get("content", ""),
            created_at=timestamp
        ))
        
    # Append default seeded items from the simulator
    for sim in vector_db.memories:
        sim_id = sim["id"]
        # Verify no duplicate id
        if not any(item.id == sim_id or item.id == f"db_{sim_id}" for item in memories):
            memories.append(MemoryResponse(
                id=sim_id,
                category=sim["category"],
                content=sim["content"],
                created_at=datetime.utcnow()
            ))

    return memories

