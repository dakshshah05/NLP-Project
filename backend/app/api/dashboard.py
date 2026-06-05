from fastapi import APIRouter, Depends
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Command, Workflow, WorkflowNode, Execution, Agent
from backend.app.security import get_current_user
from backend.app.schemas import DashboardStats, RecentActivity
from backend.app.api.agents import seed_agents_sql

router = APIRouter()

@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    uid = user["uid"]
    
    # 1. Total Commands
    total_commands = db.query(Command).filter(Command.user_id == uid).count()
    
    if total_commands == 0:
        # Seed default items in DB for first-time login
        seed_sql_mock_data(db, uid)
        total_commands = db.query(Command).filter(Command.user_id == uid).count()

    # 2. Tasks Completed (retrieve active agents task counts)
    agents = db.query(Agent).all()
    if len(agents) == 0:
        seed_agents_sql(db)
        agents = db.query(Agent).all()

    tasks_completed = sum(a.tasks_completed for a in agents)
    active_agents = sum(1 for a in agents if a.status != "Disabled")

    # 3. Success Rate
    executions = db.query(Execution).filter(Execution.user_id == uid).all()
    if executions:
        completed = sum(1 for e in executions if e.status == "Completed")
        success_rate = round((completed / len(executions)) * 100.0, 1)
    else:
        success_rate = 96.4

    # 4. Recent Activities
    recent_activities = []
    
    # Fetch recent commands
    recent_cmds = db.query(Command).filter(Command.user_id == uid).order_by(Command.created_at.desc()).limit(5).all()
    for cmd in recent_cmds:
        recent_activities.append(
            RecentActivity(
                id=cmd.id,
                type="command",
                description=f"Received NLP Command: \"{cmd.original_text[:40]}...\"",
                timestamp=cmd.created_at
            )
        )

    # Fetch recent executions
    recent_execs = db.query(Execution).filter(Execution.user_id == uid).order_by(Execution.started_at.desc()).limit(5).all()
    for ex in recent_execs:
        recent_activities.append(
            RecentActivity(
                id=ex.id,
                type="execution",
                description=f"Workflow status is {ex.status.lower()}",
                timestamp=ex.started_at
            )
        )

    recent_activities.sort(key=lambda x: x.timestamp, reverse=True)
    recent_activities = recent_activities[:6]

    # 5. Workflow statistics
    workflows = db.query(Workflow).filter(Workflow.user_id == uid).all()
    pending = 0
    running = 0
    completed = 0
    failed = 0
    
    for wf in workflows:
        if wf.status == "Pending": pending += 1
        elif wf.status == "Running": running += 1
        elif wf.status == "Completed": completed += 1
        elif wf.status == "Failed": failed += 1

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

def seed_sql_mock_data(db: Session, uid: str):
    # Seed default commands
    cmd1 = Command(
        user_id=uid,
        original_text="Send quarterly strategic updates to Priya Sharma",
        language="English",
        intent="SEND_EMAIL",
        intent_confidence=0.95,
        entities={"recipient": "Priya Sharma", "subject": "quarterly strategic updates"},
        created_at=datetime.utcnow() - timedelta(minutes=30)
    )
    cmd2 = Command(
        user_id=uid,
        original_text="Search cloud database security parameters",
        language="English",
        intent="FIND_DOCUMENT",
        intent_confidence=0.88,
        entities={"filename": "cloud database security"},
        created_at=datetime.utcnow() - timedelta(minutes=15)
    )
    
    db.add(cmd1)
    db.add(cmd2)
    db.commit()
    db.refresh(cmd1)
    db.refresh(cmd2)

    # Seed workflows
    wf1 = Workflow(
        user_id=uid,
        command_id=cmd1.id,
        name="Workflow: Send Email",
        status="Completed",
        success_rate=100.0,
        created_at=cmd1.created_at
    )
    wf2 = Workflow(
        user_id=uid,
        command_id=cmd2.id,
        name="Workflow: Find Document",
        status="Completed",
        success_rate=100.0,
        created_at=cmd2.created_at
    )
    db.add(wf1)
    db.add(wf2)
    db.commit()
    db.refresh(wf1)
    db.refresh(wf2)

    # Seed nodes
    node1 = WorkflowNode(
        workflow_id=wf1.id,
        label="NLP intent & entity parse",
        type="planner",
        status="Completed",
        inputs={},
        outputs={},
        sequence_order=0
    )
    node2 = WorkflowNode(
        workflow_id=wf2.id,
        label="NLP intent & entity parse",
        type="planner",
        status="Completed",
        inputs={},
        outputs={},
        sequence_order=0
    )
    db.add(node1)
    db.add(node2)

    # Seed executions
    exec1 = Execution(
        user_id=uid,
        workflow_id=wf1.id,
        status="Completed",
        started_at=cmd1.created_at,
        completed_at=cmd1.created_at + timedelta(seconds=5)
    )
    exec2 = Execution(
        user_id=uid,
        workflow_id=wf2.id,
        status="Completed",
        started_at=cmd2.created_at,
        completed_at=cmd2.created_at + timedelta(seconds=5)
    )
    db.add(exec1)
    db.add(exec2)
    
    db.commit()

