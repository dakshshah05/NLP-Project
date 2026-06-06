import os
import urllib.request
import urllib.parse
import json
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Form, Response, BackgroundTasks
from pydantic import BaseModel

from backend.app.firebase_config import db_firestore
from backend.app.nlp.processor import nlp_processor
from backend.app.nlp.agents_sim import AgentSimulator

router = APIRouter()

# --- Telegram Bot Webhook Request Schema ---
class TelegramChat(BaseModel):
    id: int

class TelegramMessage(BaseModel):
    chat: TelegramChat
    text: Optional[str] = None

class TelegramUpdate(BaseModel):
    message: Optional[TelegramMessage] = None


# --- Helper function to reply to Telegram ---
def reply_to_telegram(chat_id: int, text: str):
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        print("WARNING: TELEGRAM_BOT_TOKEN is not set. Skipping Telegram chat reply.")
        return
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text
    }
    data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=data,
        headers={"Content-Type": "application/json"}
    )
    try:
        with urllib.request.urlopen(req) as res:
            res.read()
        print(f"Successfully sent Telegram reply to chat_id {chat_id}")
    except Exception as e:
        print(f"ERROR: Failed to send Telegram reply: {e}")


# --- Core Logic to Trigger Workflow from Prompt ---
def trigger_agent_workflow(prompt_text: str, background_tasks: BackgroundTasks) -> str:
    print(f"Processing webhook prompt: '{prompt_text}'")
    # 1. Run NLP parsing on message body
    nlp_results = nlp_processor.process_command(prompt_text)
    intent = nlp_results.get("intent", "UNKNOWN_INTENT")
    
    # 2. Persist Command doc in Firestore under dev_mock_user_99 (dashboard visible)
    cmd_ref = db_firestore.collection("commands").document()
    cmd_data = {
        "original_text": nlp_results.get("original_text", prompt_text),
        "language": nlp_results.get("language", "English"),
        "intent": intent,
        "intent_confidence": nlp_results.get("intent_confidence", 1.0),
        "entities": nlp_results.get("entities", {}),
        "semantic_parse": nlp_results.get("semantic_parse", {}),
        "context_resolution": nlp_results.get("context_resolution", {}),
        "task_decomposition": nlp_results.get("task_decomposition", []),
        "created_at": datetime.utcnow().isoformat()
    }
    cmd_ref.set(cmd_data)

    # 3. Create Workflow Doc
    title = f"Mobile Workflow: {intent.replace('_', ' ').title()}"
    wf_ref = db_firestore.collection("workflows").document()
    wf_data = {
        "userId": "dev_mock_user_99",
        "commandId": cmd_ref.id,
        "name": title,
        "status": "Pending",
        "success_rate": 0.0,
        "created_at": datetime.utcnow().isoformat()
    }
    wf_ref.set(wf_data)

    # 4. Create Workflow Nodes
    task_decomp = nlp_results.get("task_decomposition", [])
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

    # 5. Create Execution Doc
    exec_ref = db_firestore.collection("executions").document()
    exec_data = {
        "userId": "dev_mock_user_99",
        "workflowId": wf_ref.id,
        "status": "Running",
        "started_at": datetime.utcnow().isoformat(),
        "completed_at": None,
        "logs": []
    }
    exec_ref.set(exec_data)

    # 6. Spawn Agent Simulator Asynchronously
    simulator = AgentSimulator()
    background_tasks.add_task(simulator.execute_workflow_firestore, exec_ref.id, wf_ref.id)
    
    return title


# --- Twilio WhatsApp Webhook Endpoint ---
@router.post("/twilio-whatsapp")
def twilio_whatsapp_webhook(
    background_tasks: BackgroundTasks,
    Body: str = Form(...),
    From: str = Form(...)
):
    try:
        # Trigger workflow
        workflow_title = trigger_agent_workflow(Body, background_tasks)
        
        # Build TwiML response
        reply_text = f"🤖 AURA AI: Triggered workflow '{workflow_title}'. You can monitor its live progress in your dashboard!"
    except Exception as e:
        reply_text = f"❌ AURA AI: Failed to process command. Error: {str(e)}"

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
    <Message>{reply_text}</Message>
</Response>"""
    return Response(content=twiml, media_type="application/xml")


# --- Telegram Bot Webhook Endpoint ---
@router.post("/telegram")
def telegram_webhook(
    update: TelegramUpdate,
    background_tasks: BackgroundTasks
):
    # If update doesn't have a message or text, ignore
    if not update.message or not update.message.text:
        return {"status": "ignored"}
        
    chat_id = update.message.chat.id
    prompt_text = update.message.text
    
    try:
        # Trigger workflow
        workflow_title = trigger_agent_workflow(prompt_text, background_tasks)
        reply_text = f"🤖 AURA AI: Triggered workflow '{workflow_title}'. Monitor its live progress in your dashboard!"
    except Exception as e:
        reply_text = f"❌ AURA AI: Failed to process command. Error: {str(e)}"
        
    # Send reply back to Telegram chat
    reply_to_telegram(chat_id, reply_text)
    
    return {"status": "success"}
