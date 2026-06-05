from fastapi import APIRouter, Depends, HTTPException
from typing import List
from datetime import datetime
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Command
from backend.app.security import get_current_user
from backend.app.schemas import CommandCreate, CommandResponse
from backend.app.nlp.processor import nlp_processor

router = APIRouter()

@router.post("/process", response_model=CommandResponse)
def process_user_command(
    payload: CommandCreate,
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if not payload.text.strip():
        raise HTTPException(status_code=400, detail="Command text cannot be empty")

    # Call NLP processor to perform intent/NER/decomposition
    nlp_results = nlp_processor.process_command(payload.text)

    # Prepare SQL record
    new_cmd = Command(
        user_id=user["uid"],
        original_text=nlp_results["original_text"],
        language=nlp_results["language"],
        intent=nlp_results["intent"],
        intent_confidence=nlp_results["intent_confidence"],
        entities=nlp_results["entities"],
        semantic_parse=nlp_results["semantic_parse"],
        context_resolution=nlp_results["context_resolution"],
        task_decomposition=nlp_results["task_decomposition"]
    )

    db.add(new_cmd)
    db.commit()
    db.refresh(new_cmd)

    return new_cmd

@router.get("/history", response_model=List[CommandResponse])
def get_command_history(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uid = user["uid"]
    history = db.query(Command).filter(Command.user_id == uid).order_by(Command.created_at.desc()).limit(20).all()
    return history

