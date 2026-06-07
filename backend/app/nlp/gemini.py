import os
import json
import urllib.request
import urllib.parse
from typing import Optional

def call_gemini_api(prompt: str, system_instruction: Optional[str] = None, json_mode: bool = False) -> str:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("WARNING: GEMINI_API_KEY is not set. Skipping Gemini API call.")
        return ""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    contents = [{
        "parts": [{"text": prompt}]
    }]
    
    payload = {
        "contents": contents
    }
    
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }
        
    if json_mode:
        payload["generationConfig"] = {
            "responseMimeType": "application/json"
        }
        
    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_data,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    
    try:
        # 15 seconds timeout to prevent hanging
        with urllib.request.urlopen(req, timeout=15) as res:
            resp_body = res.read().decode("utf-8")
            resp_json = json.loads(resp_body)
            
            candidates = resp_json.get("candidates", [])
            if not candidates:
                print(f"Gemini API returned no candidates. Full response: {resp_json}")
                return ""
                
            text = candidates[0].get("content", {}).get("parts", [{}])[0].get("text", "")
            return text
    except Exception as e:
        print(f"ERROR: Failed to call Gemini API: {e}")
        return ""
