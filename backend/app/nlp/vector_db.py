import re
from typing import List, Dict, Any

class VectorDatabaseSimulator:
    def __init__(self):
        # Empty memories so only custom user database memories are used
        self.memories = []

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
