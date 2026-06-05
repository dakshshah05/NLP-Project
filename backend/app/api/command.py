from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from backend.app.firebase_config import db_firestore
from backend.app.security import get_current_user
from backend.app.schemas import CommandCreate, CommandResponse
from backend.app.nlp.processor import nlp_processor

router = APIRouter()

@router.post("/process", response_model=CommandResponse)
def process_user_command(payload: CommandCreate, user: dict = Depends(get_current_user)):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Command text cannot be empty")

    # Call NLP processor to perform intent/NER/decomposition
    nlp_results = nlp_processor.process_command(payload.text)

    # Prepare Firestore document
    cmd_data = {
        "original_text": nlp_results["original_text"],
        "language": nlp_results["language"],
        "intent": nlp_results["intent"],
        "intent_confidence": nlp_results["intent_confidence"],
        "entities": nlp_results["entities"],
        "semantic_parse": nlp_results["semantic_parse"],
        "context_resolution": nlp_results["context_resolution"],
        "task_decomposition": nlp_results["task_decomposition"],
        "userId": user["uid"],
        "created_at": datetime.utcnow().isoformat()
    }

    # Write to Firestore
    cmd_ref = db_firestore.collection("commands").document()
    cmd_ref.set(cmd_data)

    return CommandResponse(
        id=cmd_ref.id,
        original_text=cmd_data["original_text"],
        language=cmd_data["language"],
        intent=cmd_data["intent"],
        intent_confidence=cmd_data["intent_confidence"],
        entities=cmd_data["entities"],
        semantic_parse=cmd_data["semantic_parse"],
        context_resolution=cmd_data["context_resolution"],
        task_decomposition=cmd_data["task_decomposition"],
        created_at=datetime.fromisoformat(cmd_data["created_at"])
    )

@router.get("/history", response_model=List[CommandResponse])
def get_command_history(user: dict = Depends(get_current_user)):
    uid = user["uid"]
    commands_ref = db_firestore.collection("commands").where("userId", "==", uid)
    docs = commands_ref.get()

    history = []
    for doc in docs:
        data = doc.to_dict()
        created_at_val = data.get("created_at")
        timestamp = datetime.fromisoformat(created_at_val) if isinstance(created_at_val, str) else datetime.utcnow()
        history.append(
            CommandResponse(
                id=doc.id,
                original_text=data.get("original_text", ""),
                language=data.get("language", "English"),
                intent=data.get("intent", ""),
                intent_confidence=data.get("intent_confidence", 1.0),
                entities=data.get("entities", {}),
                semantic_parse=data.get("semantic_parse", {}),
                context_resolution=data.get("context_resolution", {}),
                task_decomposition=data.get("task_decomposition", []),
                created_at=timestamp
            )
        )

    # Sort descending
    history.sort(key=lambda x: x.created_at, reverse=True)
    return history[:20]

