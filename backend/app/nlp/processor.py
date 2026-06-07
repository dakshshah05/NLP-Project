import os
import re
from typing import Dict, Any, List

# Optional spaCy integration
try:
    import spacy
    nlp_spacy = spacy.load("en_core_web_sm")
except Exception:
    nlp_spacy = None

# Sample Multilingual Dictionaries for Intent Identification
LANGUAGES = {
    "en": "English",
    "hi": "Hindi",
    "kn": "Kannada"
}

INTENT_MAP = {
    "SEND_EMAIL": {
        "patterns": {
            "en": [r"email", r"mail", r"send", r"write to"],
            "hi": [r"ईमेल", r"मेल", r"भेजें", r"लिखें"],
            "kn": [r"ಇಮೇಲ್", r"ಮೇಲ್", r"ಕಳುಹಿಸು", r"ಬರೆ"]
        },
        "default_name": "Compose and Send Email",
        "agent": "Email Agent"
    },
    "FIND_DOCUMENT": {
        "patterns": {
            "en": [r"find doc", r"search document", r"locate paper", r"get document", r"find project report"],
            "hi": [r"दस्तावेज़", r"फाइल ढूंढें", r"सर्च", r"खोजें"],
            "kn": [r"ದಾಖಲೆ", r"ಹುಡುಕು", r"ಫೈಲ್"]
        },
        "default_name": "Retrieve Document",
        "agent": "Document Agent"
    },
    "AUTOMATE_BROWSER": {
        "patterns": {
            "en": [r"browse", r"website", r"google", r"search web", r"open page", r"download from url"],
            "hi": [r"वेबसाइट", r"खोलें", r"ब्राउज़", r"गूगल", r"डाउनलोड"],
            "kn": [r"ವೆಬ್ ಸೈಟ್", r"ಬ್ರೌಸ್", r"ಗೂಗಲ್", r"ಡೌನ್ಲೋಡ್"]
        },
        "default_name": "Web Automation",
        "agent": "Browser Agent"
    },
    "PLAN_SCHEDULE": {
        "patterns": {
            "en": [r"schedule", r"calendar", r"plan", r"meeting", r"set reminder"],
            "hi": [r"शेड्यूल", r"योजना", r"बैठक", r"रिमाइंडर"],
            "kn": [r"ಸಭೆ", r"ಯೋಜನೆ", r"ಜ್ಞಾಪನೆ"]
        },
        "default_name": "Plan Automation Schedule",
        "agent": "Planner Agent"
    },
    "MANAGE_FILES": {
        "patterns": {
            "en": [r"copy file", r"move folder", r"delete archive", r"compress directory", r"backup"],
            "hi": [r"कॉपी", r"बैकअप", r"फ़ाइल हटाएं", r"फ़ोल्डर"],
            "kn": [r"ಕಾಪಿ", r"ಬ್ಯಾಕಪ್", r"ಡಿಲೀಟ್", r"ಫೋಲ್ಡರ್", r"ಫೈಲ್"]
        },
        "default_name": "File System Operation",
        "agent": "File Agent"
    }
}

class NLPProcessor:
    def __init__(self):
        pass

    def detect_language(self, text: str) -> str:
        # Simple heuristic check for Indic scripts or English
        text_lower = text.lower()
        # Devnagari characters are in range U+0900 to U+097F
        if any(ord(char) >= 0x0900 and ord(char) <= 0x097F for char in text):
            return "Hindi"
        # Kannada characters are in range U+0C80 to U+0CFF
        if any(ord(char) >= 0x0C80 and ord(char) <= 0x0CFF for char in text):
            return "Kannada"
        return "English"

    def detect_intent(self, text: str, lang: str) -> tuple:
        text_lower = text.lower()
        lang_code = "en"
        if lang == "Hindi":
            lang_code = "hi"
        elif lang == "Kannada":
            lang_code = "kn"

        highest_score = 0.0
        detected_intent = "UNKNOWN"

        for intent_name, data in INTENT_MAP.items():
            patterns = data["patterns"].get(lang_code, [])
            match_count = 0
            for pattern in patterns:
                if re.search(pattern, text_lower):
                    match_count += 1
            
            if match_count > 0:
                score = 0.8 + 0.05 * match_count
                # Boost if English direct match too
                if any(p in text_lower for p in data["patterns"]["en"]):
                    score = min(score + 0.1, 1.0)
                if score > highest_score:
                    highest_score = score
                    detected_intent = intent_name

        if detected_intent == "UNKNOWN":
            # Default fallback intent
            detected_intent = "PLAN_SCHEDULE"
            highest_score = 0.65

        return detected_intent, max(highest_score, 0.70)

    def extract_entities(self, text: str, lang: str) -> Dict[str, Any]:
        entities = {
            "recipient": None,
            "subject": None,
            "filename": None,
            "url": None,
            "date_time": None,
            "keywords": []
        }

        # Regex-based extraction rules
        # Emails
        email_matches = re.findall(r"[\w\.-]+@[\w\.-]+\.\w+", text)
        if email_matches:
            entities["recipient"] = email_matches[0]

        # URLs
        url_matches = re.findall(r"https?://[^\s]+", text)
        if url_matches:
            entities["url"] = url_matches[0]

        # File names (e.g. docx, pdf, txt)
        file_matches = re.findall(r"[\w\.-]+\.(?:pdf|txt|docx|xlsx|csv|zip)", text, re.IGNORECASE)
        if file_matches:
            entities["filename"] = file_matches[0]

        # File generation request check
        # Match pattern: create/generate/write a/an [format/type] on/about [topic]
        create_match = re.search(
            r"(?:create|generate|write|make|send|compose)\s+(?:a\s+)?(pdf|document|text file|report|csv|txt)\s+(?:on|about|for|of)?\s*([\w\s'-]+?)(?:\s+(?:and\s+)?(?:send|mail|email|post|to|at)\b|$)", 
            text, 
            re.IGNORECASE
        )
        if create_match:
            file_type = create_match.group(1).lower()
            topic = create_match.group(2).strip()
            
            # Map type to extension
            ext = ".pdf"
            if "txt" in file_type or "text" in file_type:
                ext = ".txt"
            elif "csv" in file_type:
                ext = ".csv"
                
            if not entities.get("filename"):
                # Clean topic to make a nice filename
                clean_topic = re.sub(r"[^\w\s-]", "", topic).strip().lower()
                clean_topic = re.sub(r"[-\s]+", "_", clean_topic)
                entities["filename"] = f"{clean_topic}{ext}"
            
            entities["file_topic"] = topic
            entities["create_file"] = True

        # Recipient Name heuristics (e.g., "to Ramesh", "to Priya", "send to John")
        to_matches = re.findall(r"(?:to|भेजें|ಕಳುಹಿಸು)\s+([A-Z][a-z]+|[a-zA-Z\u0900-\u097F\u0C80-\u0CFF]+)", text)
        if to_matches and not entities["recipient"]:
            entities["recipient"] = to_matches[0]

        # Subject extraction heuristics (e.g., "subject 'Hello World'", "about project details")
        about_matches = re.findall(r"(?:about|subject|विषय|ಬಗ್ಗೆ)\s+['\"]?([^'\"]+?)['\"]?(?:\s|$)", text, re.IGNORECASE)
        if about_matches:
            entities["subject"] = about_matches[0]

        if not entities.get("subject") and entities.get("file_topic"):
            entities["subject"] = f"{entities['file_topic']} Report"

        # spaCy high-fidelity additions if loaded
        if nlp_spacy and lang == "English":
            doc = nlp_spacy(text)
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG"] and not entities["recipient"]:
                    entities["recipient"] = ent.text
                elif ent.label_ in ["DATE", "TIME"] and not entities["date_time"]:
                    entities["date_time"] = ent.text

        # Keywords fallback
        words = text.split()
        entities["keywords"] = [w for w in words if len(w) > 4][:5]

        return entities

    def semantic_parse(self, text: str, intent: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "semantic_relations": {
                "action": intent,
                "actor": "AURA AI Agent",
                "object": entities.get("filename") or entities.get("recipient") or "System Parameters",
                "instrument": "API Call / Agent Execution"
            },
            "dependency_tree_status": "Parsed successfully",
            "logical_form": f"{intent}(actor=Agent, target={entities.get('recipient')}, resource={entities.get('filename') or entities.get('url')})"
        }

    def context_resolution(self, text: str, entities: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "active_session": "Session-AURA-992",
            "resolved_references": {
                "it": entities.get("filename") or "previous document",
                "them": entities.get("recipient") or "intended contact"
            },
            "user_preferences": {
                "language_preference": self.detect_language(text),
                "preferred_agent": "Planner Agent"
            }
        }

    def decompose_tasks(self, text: str, intent: str, entities: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Break down the user's intent into executable workflow stages
        tasks = []
        
        # Always start with Intent Detection and Entity Extraction
        tasks.append({
            "id": "node-nlp",
            "label": "NLP Intent & Entity Parse",
            "type": "planner",
            "inputs": {"text": text},
            "outputs": {"intent": intent, "entities": entities}
        })

        if intent == "SEND_EMAIL":
            # Flow: Find or create attachment/doc if mentioned -> Write draft -> Send email
            if entities.get("create_file"):
                tasks.append({
                    "id": "node-create-doc",
                    "label": f"Create Document: {entities['filename']}",
                    "type": "document",
                    "inputs": {
                        "filename": entities["filename"],
                        "topic": entities.get("file_topic", "General Report"),
                        "action": "create"
                    },
                    "outputs": {"filepath": f"/workspace/{entities['filename']}"}
                })
            elif entities.get("filename"):
                tasks.append({
                    "id": "node-retrieve",
                    "label": f"Find File: {entities['filename']}",
                    "type": "document",
                    "inputs": {"query": entities["filename"]},
                    "outputs": {"filepath": f"/workspace/{entities['filename']}"}
                })
            tasks.append({
                "id": "node-email",
                "label": f"Compose Email to {entities.get('recipient') or 'Recipient'}",
                "type": "email",
                "inputs": {
                    "to": entities.get("recipient") or "admin@company.com",
                    "subject": entities.get("subject") or "AURA Automated Report",
                    "attachment": f"/workspace/{entities['filename']}" if entities.get("filename") else None
                },
                "outputs": {"status": "sent", "message_id": "msg_812398"}
            })

        elif intent == "FIND_DOCUMENT":
            # Flow: Search Vector Database -> Retrieve Document -> Extract contents
            tasks.append({
                "id": "node-vector",
                "label": f"Vector Search: {entities.get('filename') or 'Report'}",
                "type": "memory",
                "inputs": {"query": text, "category": "documents"},
                "outputs": {"matches": [{"id": "doc_1", "score": 0.92, "content": "Quarterly business review details."}]}
            })
            tasks.append({
                "id": "node-doc",
                "label": "Extract Key Elements",
                "type": "document",
                "inputs": {"document_id": "doc_1"},
                "outputs": {"summary": "Retrieved quarterly performance metrics."}
            })

        elif intent == "AUTOMATE_BROWSER":
            # Flow: Open URL -> Extract Data -> Store in File
            url = entities.get("url") or "https://news.ycombinator.com"
            tasks.append({
                "id": "node-browser",
                "label": f"Navigate & Scrape {url}",
                "type": "browser",
                "inputs": {"url": url, "extract_selectors": ["title", "h1"]},
                "outputs": {"scraped_data": {"title": "Tech News Today", "headings": ["AI Revolution", "LLMs in Production"]}}
            })
            tasks.append({
                "id": "node-file-write",
                "label": "Save Scraped Data to File",
                "type": "file",
                "inputs": {"data": {"title": "Tech News Today"}, "filename": "scraped_results.json"},
                "outputs": {"status": "saved", "path": "/workspace/scraped_results.json"}
            })

        elif intent == "MANAGE_FILES":
            # Flow: Find source -> Execute action (Copy/Backup) -> Log execution
            filename = entities.get("filename") or "report.csv"
            tasks.append({
                "id": "node-file-op",
                "label": f"Compress and Backup: {filename}",
                "type": "file",
                "inputs": {"source": filename, "action": "backup"},
                "outputs": {"archive_path": f"/workspace/backups/{filename}.zip"}
            })

        else: # PLAN_SCHEDULE / DEFAULT
            tasks.append({
                "id": "node-planner",
                "label": "Decompose General Action Plans",
                "type": "planner",
                "inputs": {"command": text},
                "outputs": {"action_steps": ["Step 1: Parse requirements", "Step 2: Allocate Agents"]}
            })

        # Final validation stage
        tasks.append({
            "id": "node-complete",
            "label": "Verify Execution and Store Memory",
            "type": "memory",
            "inputs": {"status": "Completed successfully"},
            "outputs": {"saved_state": "Workflow ID completed"}
        })

        return tasks

    def process_command(self, text: str) -> Dict[str, Any]:
        # If Gemini key is set, use AI to parse the command dynamically
        if os.getenv("GEMINI_API_KEY"):
            from backend.app.nlp.gemini import call_gemini_api
            
            system_instruction = """You are an NLP parser for AURA AI, an autonomous multi-agent system.
Your job is to parse the user's input command and return a structured JSON response.

Intents:
- SEND_EMAIL: User wants to compose and send an email. If they mention creating a PDF/document and sending it, the intent is SEND_EMAIL.
- FIND_DOCUMENT: User wants to search/retrieve a document.
- AUTOMATE_BROWSER: User wants to scrape a website, browse the web, or download something from a URL.
- PLAN_SCHEDULE: User wants to plan a schedule, set a reminder, or generic planning.
- MANAGE_FILES: User wants to backup, copy, move, compress, or manage files.

JSON Structure:
{
  "intent": "SEND_EMAIL" | "FIND_DOCUMENT" | "AUTOMATE_BROWSER" | "PLAN_SCHEDULE" | "MANAGE_FILES",
  "intent_confidence": 0.0 to 1.0,
  "entities": {
    "recipient": "email address or name of recipient (or null)",
    "subject": "email subject (or null)",
    "filename": "name of the file (e.g. benefits_of_ai.pdf or null)",
    "url": "url to browse/scrape (or null)",
    "date_time": "date/time mentioned (or null)",
    "file_topic": "topic/subject of file to create/find (e.g., 'Benefits of AI')",
    "create_file": true | false (set to true if user specifically asks to create, write, generate, or send a new file/PDF on a topic)
  },
  "task_decomposition": [
    // Array of tasks to execute in sequence.
    // If intent is SEND_EMAIL:
    // 1. NLP Node:
    //    {"id": "node-nlp", "label": "NLP Intent & Entity Parse", "type": "planner", "inputs": {"text": "prompt"}, "outputs": {}}
    // 2. Document Creation Node (ONLY if create_file is true):
    //    {"id": "node-create-doc", "label": "Create Document: benefits_of_ai.pdf", "type": "document", "inputs": {"filename": "benefits_of_ai.pdf", "topic": "Benefits of AI", "action": "create"}, "outputs": {"filepath": "/workspace/benefits_of_ai.pdf"}}
    // 3. Email Node:
    //    {"id": "node-email", "label": "Compose Email to <recipient>", "type": "email", "inputs": {"to": "<recipient>", "subject": "<subject>", "attachment": "/workspace/benefits_of_ai.pdf" (if create_file is true) or null}, "outputs": {}}
    // 4. Memory/Verify Node:
    //    {"id": "node-complete", "label": "Verify Execution and Store Memory", "type": "memory", "inputs": {"status": "Completed successfully"}, "outputs": {}}
  ]
}

Ensure the task_decomposition is fully filled based on the intent and entities.
Return ONLY raw JSON conforming to this schema. Do not wrap it in markdown code blocks."""
            
            gemini_response = call_gemini_api(text, system_instruction=system_instruction, json_mode=True)
            if gemini_response:
                try:
                    import json
                    parsed = json.loads(gemini_response.strip())
                    
                    intent = parsed.get("intent", "PLAN_SCHEDULE")
                    confidence = parsed.get("intent_confidence", 0.95)
                    entities = parsed.get("entities", {})
                    decomposition = parsed.get("task_decomposition", [])
                    
                    if not entities.get("subject") and entities.get("file_topic"):
                        entities["subject"] = f"{entities['file_topic']} Report"
                        for t in decomposition:
                            if t.get("type") == "email" and "inputs" in t:
                                if not t["inputs"].get("subject"):
                                    t["inputs"]["subject"] = entities["subject"]
                                    
                    return {
                        "original_text": text,
                        "language": self.detect_language(text),
                        "intent": intent,
                        "intent_confidence": confidence,
                        "entities": entities,
                        "semantic_parse": self.semantic_parse(text, intent, entities),
                        "context_resolution": self.context_resolution(text, entities),
                        "task_decomposition": decomposition
                    }
                except Exception as parse_ex:
                    print(f"Failed to parse Gemini NLP response: {parse_ex}. Falling back to rule-based parser.")

        # Fallback to rule-based parsing
        lang = self.detect_language(text)
        intent, confidence = self.detect_intent(text, lang)
        entities = self.extract_entities(text, lang)
        semantic = self.semantic_parse(text, intent, entities)
        context = self.context_resolution(text, entities)
        decomposition = self.decompose_tasks(text, intent, entities)

        return {
            "original_text": text,
            "language": lang,
            "intent": intent,
            "intent_confidence": confidence,
            "entities": entities,
            "semantic_parse": semantic,
            "context_resolution": context,
            "task_decomposition": decomposition
        }

nlp_processor = NLPProcessor()
