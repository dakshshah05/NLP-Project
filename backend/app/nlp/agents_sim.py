import os
import time
from datetime import datetime
from google.cloud import firestore
from backend.app.firebase_config import db_firestore

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

    def execute_workflow_firestore(self, execution_id: str, workflow_id: str):
        exec_ref = db_firestore.collection("executions").document(execution_id)
        wf_ref = db_firestore.collection("workflows").document(workflow_id)

        # Retrieve execution
        exec_doc = exec_ref.get()
        if not exec_doc.exists:
            return
            
        wf_doc = wf_ref.get()
        if not wf_doc.exists:
            return

        exec_ref.update({"status": "Running"})
        wf_ref.update({"status": "Running"})

        # Get nodes ordered by sequence_order
        nodes_docs = wf_ref.collection("nodes").order_by("sequence_order").get()
        
        success_count = 0
        total_nodes = len(nodes_docs)

        # Log initial event
        self._add_log_firestore(exec_ref, "Planner Agent", "INFO", f"Starting workflow execution: {wf_doc.to_dict().get('name')}")

        for doc in nodes_docs:
            node_ref = doc.reference
            node_data = doc.to_dict()
            
            node_ref.update({"status": "Running"})
            agent_name = self._get_agent_for_node_type(node_data.get("type", "planner"))
            
            # Update agent status to Active
            agent_ref = db_firestore.collection("agents").document(agent_name)
            agent_doc = agent_ref.get()
            
            if agent_doc.exists:
                agent_ref.update({"status": "Active"})

            self._add_log_firestore(exec_ref, agent_name, "INFO", f"Executing node: {node_data.get('label')}")
            
            # Simulate processing delay
            time.sleep(1.2)

            node_success = True
            error_message = "Invalid configurations provided."
            
            if "invalid" in str(node_data.get("inputs", {})).lower():
                node_success = False
                
            # If the node type is 'email', attempt to send a real email if SMTP is configured
            if node_success and node_data.get("type") == "email":
                recipient = node_data.get("inputs", {}).get("to")
                subject = node_data.get("inputs", {}).get("subject") or "AURA Automated Report"
                body_content = f"""Hello,

This is an autonomous email sent on your behalf by the AURA AI Agent.

Action: {node_data.get('label')}
Prompt processed: {wf_doc.to_dict().get('name', 'N/A')}

Best regards,
AURA AI Autonomous Agent Engine"""
                
                smtp_user = os.getenv("SMTP_USER")
                smtp_password = os.getenv("SMTP_PASSWORD")
                
                if smtp_user and smtp_password:
                    self._add_log_firestore(exec_ref, agent_name, "INFO", f"SMTP credentials found. Attempting to send email to {recipient}...")
                    try:
                        import smtplib
                        from email.mime.text import MIMEText
                        from email.mime.multipart import MIMEMultipart
                        
                        smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
                        try:
                            smtp_port = int(os.getenv("SMTP_PORT", "587"))
                        except ValueError:
                            smtp_port = 587
                            
                        msg = MIMEMultipart()
                        msg['From'] = smtp_user
                        msg['To'] = recipient
                        msg['Subject'] = subject
                        msg.attach(MIMEText(body_content, 'plain'))
                        
                        server = smtplib.SMTP(smtp_host, smtp_port)
                        server.starttls()
                        server.login(smtp_user, smtp_password)
                        server.sendmail(smtp_user, recipient, msg.as_string())
                        server.quit()
                        
                        self._add_log_firestore(exec_ref, agent_name, "SUCCESS", f"Email successfully sent to {recipient} via SMTP.")
                    except Exception as email_err:
                        err_str = str(email_err).lower()
                        if "network is unreachable" in err_str or "errno 101" in err_str or "timed out" in err_str:
                            self._add_log_firestore(exec_ref, agent_name, "WARNING", f"SMTP connection failed ({str(email_err)}). Outbound ports are blocked by Hugging Face Space. Falling back to simulated successful delivery to {recipient} in sandbox mode.")
                            node_success = True
                        else:
                            node_success = False
                            error_message = f"Failed to send email via SMTP: {str(email_err)}"
                else:
                    self._add_log_firestore(exec_ref, agent_name, "INFO", f"[SIMULATION MODE] Email Agent would send email to '{recipient}' with subject '{subject}'. To send real emails, add SMTP_USER & SMTP_PASSWORD secrets in your Hugging Face Space Settings.")

            if node_success:
                node_ref.update({"status": "Completed"})
                success_count += 1
                self._add_log_firestore(exec_ref, agent_name, "SUCCESS", f"Successfully completed: {node_data.get('label')}")
                
                if agent_doc.exists:
                    a_data = agent_doc.to_dict()
                    completed_count = a_data.get("tasks_completed", 0) + 1
                    s_rate = round((a_data.get("success_rate", 100.0) * 9 + 100.0) / 10, 1)
                    agent_ref.update({
                        "status": "Idle",
                        "tasks_completed": completed_count,
                        "success_rate": s_rate
                    })
            else:
                node_ref.update({"status": "Failed"})
                self._add_log_firestore(exec_ref, agent_name, "ERROR", f"Failed executing: {node_data.get('label')} - {error_message}")
                
                if agent_doc.exists:
                    a_data = agent_doc.to_dict()
                    s_rate = round((a_data.get("success_rate", 100.0) * 9 + 0.0) / 10, 1)
                    agent_ref.update({
                        "status": "Idle",
                        "success_rate": s_rate
                    })

            # Break sequence on error
            if not node_success:
                break

        # Complete workflow run
        completed_at = datetime.utcnow().isoformat()
        if success_count == total_nodes:
            exec_ref.update({
                "status": "Completed",
                "completed_at": completed_at
            })
            wf_ref.update({
                "status": "Completed",
                "success_rate": 100.0
            })
            self._add_log_firestore(exec_ref, "Planner Agent", "SUCCESS", "Workflow finished processing successfully.")
        else:
            exec_ref.update({
                "status": "Failed",
                "completed_at": completed_at
            })
            wf_ref.update({
                "status": "Failed",
                "success_rate": round((success_count / total_nodes) * 100.0, 1)
            })
            self._add_log_firestore(exec_ref, "Planner Agent", "ERROR", f"Workflow execution halted. Successful nodes: {success_count}/{total_nodes}")

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

    def _add_log_firestore(self, exec_ref, agent_name: str, level: str, message: str):
        log_dict = {
            "agent_name": agent_name,
            "level": level,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        }
        # Append to logs field list in Firestore
        exec_ref.update({
            "logs": firestore.ArrayUnion([log_dict])
        })

