import os
import json
import urllib.request
import urllib.parse
from typing import Optional

def call_groq_api(prompt: str, system_instruction: Optional[str] = None, json_mode: bool = False) -> str:
    """
    Call Groq Cloud API (Free Tier: 14,400 requests/day).
    Uses Llama-3.3-70B-Versatile for state-of-the-art multilingual understanding (Hindi, Kannada, English, Hinglish).
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        print("WARNING: GROQ_API_KEY is not set. Skipping Groq API call.")
        return ""

    url = "https://api.groq.com/openai/v1/chat/completions"
    
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": messages,
        "temperature": 0.1,
    }
    
    if json_mode:
        payload["response_format"] = {"type": "json_object"}

    req_data = json.dumps(payload).encode("utf-8")
    req = urllib.request.Request(
        url,
        data=req_data,
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=15) as res:
            resp_body = res.read().decode("utf-8")
            resp_json = json.loads(resp_body)
            choices = resp_json.get("choices", [])
            if not choices:
                print(f"Groq API returned no choices: {resp_json}")
                return ""
            content = choices[0].get("message", {}).get("content", "")
            return content
    except Exception as e:
        print(f"ERROR: Failed to call Groq API: {e}")
        return ""
