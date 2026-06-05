from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from backend.app.firebase_config import db_firestore
from backend.app.security import get_current_user
from backend.app.schemas import DashboardStats, RecentActivity

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(user: dict = Depends(get_current_user)):
    uid = user["uid"]
    
    # 1. Total Commands
    commands_ref = db_firestore.collection("commands").where("userId", "==", uid)
    commands_docs = commands_ref.get()
    total_commands = len(commands_docs)
    
    if total_commands == 0:
        # Seed default items in Firestore for first-time login
        seed_firestore_mock_data(uid)
        commands_docs = commands_ref.get()
        total_commands = len(commands_docs)

    # 2. Tasks Completed (retrieve active agents task counts)
    agents_ref = db_firestore.collection("agents")
    agents_docs = agents_ref.get()
    
    # Auto-seed agents if empty
    if len(agents_docs) == 0:
        seed_agents_firestore()
        agents_docs = agents_ref.get()

    tasks_completed = sum(doc.to_dict().get("tasks_completed", 0) for doc in agents_docs)
    active_agents = sum(1 for doc in agents_docs if doc.to_dict().get("status") != "Disabled")

    # 3. Success Rate
    executions_ref = db_firestore.collection("executions").where("userId", "==", uid)
    executions_docs = executions_ref.get()
    
    if executions_docs:
        completed = sum(1 for doc in executions_docs if doc.to_dict().get("status") == "Completed")
        success_rate = round((completed / len(executions_docs)) * 100.0, 1)
    else:
        success_rate = 96.4

    # 4. Recent Activities
    recent_activities = []
    
    # Fetch recent commands
    sorted_cmds = sorted(commands_docs, key=lambda x: x.to_dict().get("created_at", ""), reverse=True)[:5]
    for doc in sorted_cmds:
        data = doc.to_dict()
        created_at_val = data.get("created_at")
        timestamp = datetime.fromisoformat(created_at_val) if isinstance(created_at_val, str) else datetime.utcnow()
        recent_activities.append(
            RecentActivity(
                id=doc.id,
                type="command",
                description=f"Received NLP Command: \"{data.get('original_text', '')[:40]}...\"",
                timestamp=timestamp
            )
        )

    # Fetch recent executions
    sorted_execs = sorted(executions_docs, key=lambda x: x.to_dict().get("started_at", ""), reverse=True)[:5]
    for doc in sorted_execs:
        data = doc.to_dict()
        started_at_val = data.get("started_at")
        timestamp = datetime.fromisoformat(started_at_val) if isinstance(started_at_val, str) else datetime.utcnow()
        recent_activities.append(
            RecentActivity(
                id=doc.id,
                type="execution",
                description=f"Workflow status is {data.get('status', 'Pending').lower()}",
                timestamp=timestamp
            )
        )

    recent_activities.sort(key=lambda x: x.timestamp, reverse=True)
    recent_activities = recent_activities[:6]

    # 5. Workflow statistics
    workflows_ref = db_firestore.collection("workflows").where("userId", "==", uid)
    workflows_docs = workflows_ref.get()
    
    pending = 0
    running = 0
    completed = 0
    failed = 0
    
    for doc in workflows_docs:
        status_val = doc.to_dict().get("status", "Pending")
        if status_val == "Pending": pending += 1
        elif status_val == "Running": running += 1
        elif status_val == "Completed": completed += 1
        elif status_val == "Failed": failed += 1

    workflow_stats = {
        "pending": pending,
        "running": running,
        "completed": completed,
        "failed": failed
    }

    return DashboardStats(
        total_commands=total_commands,
        tasks_completed=tasks_completed,
        active_agents=active_agents,
        success_rate=success_rate,
        recent_activities=recent_activities,
        workflow_stats=workflow_stats
    )

def seed_agents_firestore():
    from backend.app.nlp.agents_sim import AGENT_CAPABILITIES
    for name, capabilities in AGENT_CAPABILITIES.items():
        db_firestore.collection("agents").document(name).set({
            "name": name,
            "status": "Idle",
            "tasks_completed": 4 if "Planner" in name else 2,
            "success_rate": 100.0,
            "capabilities": capabilities
        })

def seed_firestore_mock_data(uid: str):
    # Seed default command
    commands_data = [
        {"original_text": "Send quarterly strategic updates to Priya Sharma", "language": "English", "intent": "SEND_EMAIL", "intent_confidence": 0.95, "entities": {"recipient": "Priya Sharma", "subject": "quarterly strategic updates"}, "created_at": (datetime.utcnow() - timedelta(minutes=30)).isoformat(), "userId": uid},
        {"original_text": "Search cloud database security parameters", "language": "English", "intent": "FIND_DOCUMENT", "intent_confidence": 0.88, "entities": {"filename": "cloud database security"}, "created_at": (datetime.utcnow() - timedelta(minutes=15)).isoformat(), "userId": uid}
    ]
    
    for cmd in commands_data:
        cmd_ref = db_firestore.collection("commands").document()
        cmd_ref.set(cmd)
        
        # Seed associated workflow
        wf_ref = db_firestore.collection("workflows").document()
        wf_ref.set({
            "userId": uid,
            "commandId": cmd_ref.id,
            "name": f"Workflow: {cmd['intent'].replace('_', ' ').title()}",
            "status": "Completed",
            "success_rate": 100.0,
            "created_at": cmd["created_at"]
        })
        
        # Seed nodes
        # Add basic nlp node & execute node
        db_firestore.collection("workflows").document(wf_ref.id).collection("nodes").document("node-1").set({
            "id": "node-1",
            "workflow_id": wf_ref.id,
            "label": "NLP intent & entity parse",
            "type": "planner",
            "status": "Completed",
            "inputs": {},
            "outputs": {},
            "sequence_order": 0
        })

        # Seed executions
        db_firestore.collection("executions").document().set({
            "userId": uid,
            "workflowId": wf_ref.id,
            "status": "Completed",
            "started_at": cmd["created_at"],
            "completed_at": (datetime.fromisoformat(cmd["created_at"]) + timedelta(seconds=5)).isoformat()
        })

