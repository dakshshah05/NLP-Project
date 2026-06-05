import re
from typing import List, Dict, Any

class VectorDatabaseSimulator:
    def __init__(self):
        # Seed some default values
        self.memories = [
            # Contacts
            {"id": "c1", "category": "contacts", "content": "Priya Sharma - Senior Product Owner (email: priya.sharma@aura.ai, phone: +91 98765 43210)"},
            {"id": "c2", "category": "contacts", "content": "Ramesh Kumar - DevOps Director (email: ramesh.k@aura.ai, office: Bangalore HQ)"},
            {"id": "c3", "category": "contacts", "content": "John Doe - Client Support Coordinator (email: j.doe@external.com)"},
            # Known Documents
            {"id": "d1", "category": "documents", "content": "Q3 Enterprise Strategy Report: Highlighting integration of Ollama, spaCy, and PostgreSQL vectors for client productivity automations."},
            {"id": "d2", "category": "documents", "content": "Security Audit Guidelines v2: Documenting PostgreSQL database security policies, ChromaDB authorization standards, and SSL configurations."},
            {"id": "d3", "category": "documents", "content": "Email Marketing Playbook: Draft blueprints and email templates for weekly customer engagement operations."},
            # User Preferences
            {"id": "p1", "category": "preferences", "content": "Language Preference: English (Primary), Hindi (Secondary), Kannada (Tertiary)"},
            {"id": "p2", "category": "preferences", "content": "Default Execution Agent: Planner Agent"},
            {"id": "p3", "category": "preferences", "content": "Theme preference: Dark Mode (Glassmorphism UI active)"},
            # Previous Commands
            {"id": "cmd1", "category": "commands", "content": "Send Q3 Strategy Report to Priya Sharma via email"},
            {"id": "cmd2", "category": "commands", "content": "Check website https://news.ycombinator.com and backup titles to report.csv"},
            {"id": "cmd3", "category": "commands", "content": "Compress workspace log documents and email to Ramesh Kumar"}
        ]

    def add_item(self, category: str, content: str) -> Dict[str, Any]:
        item_id = f"custom_{len(self.memories) + 1}"
        item = {"id": item_id, "category": category, "content": content}
        self.memories.append(item)
        return item

    def search(self, query: str, category: str = None) -> List[Dict[str, Any]]:
        query_words = set(re.findall(r"\w+", query.lower()))
        results = []

        for item in self.memories:
            if category and item["category"] != category:
                continue

            content_words = set(re.findall(r"\w+", item["content"].lower()))
            overlap = query_words.intersection(content_words)
            
            # Simple Jaccard similarity score logic
            if overlap:
                score = len(overlap) / len(query_words.union(content_words))
                # Boost match score slightly for exact substring matches
                if query.lower() in item["content"].lower():
                    score = min(score + 0.35, 1.0)
                score = round(max(score, 0.15), 2)
            else:
                # Basic context similarity simulation if words don't directly match
                if any(w in item["content"].lower() for w in ["email", "report", "strategy"]) and any(qw in query.lower() for qw in ["mail", "paper", "doc"]):
                    score = 0.45
                else:
                    score = 0.0

            if score > 0.05:
                results.append({
                    "id": item["id"],
                    "category": item["category"],
                    "content": item["content"],
                    "score": score
                })

        # Sort by similarity score descending
        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:5]

vector_db = VectorDatabaseSimulator()
