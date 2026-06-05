import time
from datetime import datetime
from backend.app.database import SessionLocal
from backend.app.models import Workflow, WorkflowNode, Execution, ExecutionLog, Agent

AGENT_CAPABILITIES = {
    "Planner Agent": ["Task decomposition", "Intent mapping", "Workflow routing"],
    "Document Agent": ["Content summarization", "Entity matching", "Parsing PDF/CSV"],
    "Email Agent": ["SMTP connections", "Draft composing", "Spam analysis"],
    "Browser Agent": ["HTML scraping", "Form submission", "Session navigation"],
    "File Agent": ["Directory backup", "JSON/CSV exports", "File compression"],
    "Memory Agent": ["Vector storage", "Retrieval augmented generation", "Preferences matching"]
}

class AgentSimulator:
    def __init__(self):
        pass

    def execute_workflow_sql(self, execution_id: str, workflow_id: str):
        db = SessionLocal()
        try:
            exec_obj = db.query(Execution).filter(Execution.id == execution_id).first()
            wf_obj = db.query(Workflow).filter(Workflow.id == workflow_id).first()

            if not exec_obj or not wf_obj:
                return

            exec_obj.status = "Running"
            wf_obj.status = "Running"
            db.commit()

            # Get nodes ordered by sequence_order
            nodes = db.query(WorkflowNode).filter(WorkflowNode.workflow_id == workflow_id).order_by(WorkflowNode.sequence_order).all()
            
            success_count = 0
            total_nodes = len(nodes)

            # Log initial event
            self._add_log_sql(db, execution_id, "Planner Agent", "INFO", f"Starting workflow execution: {wf_obj.name}")

            for node in nodes:
                node.status = "Running"
                db.commit()
                
                agent_name = self._get_agent_for_node_type(node.type)
                
                # Update agent status to Active
                agent = db.query(Agent).filter(Agent.name == agent_name).first()
                if agent:
                    agent.status = "Active"
                    db.commit()

                self._add_log_sql(db, execution_id, agent_name, "INFO", f"Executing node: {node.label}")
                
                # Simulate processing delay
                time.sleep(1.2)

                node_success = True
                if "invalid" in str(node.inputs).lower():
                    node_success = False

                if node_success:
                    node.status = "Completed"
                    success_count += 1
                    self._add_log_sql(db, execution_id, agent_name, "SUCCESS", f"Successfully completed: {node.label}")
                    
                    if agent:
                        completed_count = agent.tasks_completed + 1
                        s_rate = round((agent.success_rate * 9 + 100.0) / 10, 1)
                        agent.status = "Idle"
                        agent.tasks_completed = completed_count
                        agent.success_rate = s_rate
                        db.commit()
                else:
                    node.status = "Failed"
                    self._add_log_sql(db, execution_id, agent_name, "ERROR", f"Failed executing: {node.label} - Invalid configurations provided.")
                    
                    if agent:
                        s_rate = round((agent.success_rate * 9 + 0.0) / 10, 1)
                        agent.status = "Idle"
                        agent.success_rate = s_rate
                        db.commit()

                # Break sequence on error
                if not node_success:
                    break

            # Complete workflow run
            completed_at = datetime.utcnow()
            if success_count == total_nodes:
                exec_obj.status = "Completed"
                exec_obj.completed_at = completed_at
                wf_obj.status = "Completed"
                wf_obj.success_rate = 100.0
                self._add_log_sql(db, execution_id, "Planner Agent", "SUCCESS", "Workflow finished processing successfully.")
            else:
                exec_obj.status = "Failed"
                exec_obj.completed_at = completed_at
                wf_obj.status = "Failed"
                wf_obj.success_rate = round((success_count / total_nodes) * 100.0, 1)
                self._add_log_sql(db, execution_id, "Planner Agent", "ERROR", f"Workflow execution halted. Successful nodes: {success_count}/{total_nodes}")

            db.commit()
        except Exception as e:
            print(f"Background simulator error: {e}")
        finally:
            db.close()

    def _get_agent_for_node_type(self, node_type: str) -> str:
        mapping = {
            "planner": "Planner Agent",
            "document": "Document Agent",
            "email": "Email Agent",
            "browser": "Browser Agent",
            "file": "File Agent",
            "memory": "Memory Agent"
        }
        return mapping.get(node_type, "Planner Agent")

    def _add_log_sql(self, db, execution_id: str, agent_name: str, level: str, message: str):
        new_log = ExecutionLog(
            execution_id=execution_id,
            agent_name=agent_name,
            level=level,
            message=message
        )
        db.add(new_log)
        db.commit()

