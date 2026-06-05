import os
import firebase_admin
from firebase_admin import credentials

PROJECT_ID = os.getenv("FIREBASE_PROJECT_ID")
CLIENT_EMAIL = os.getenv("FIREBASE_CLIENT_EMAIL")
# Replace escaped newlines in Render/Koyeb secret manager
PRIVATE_KEY = os.getenv("FIREBASE_PRIVATE_KEY", "").replace("\\n", "\n")

# Initialize Admin SDK for Token Verification
if PROJECT_ID and CLIENT_EMAIL and PRIVATE_KEY:
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": PROJECT_ID,
                "private_key": PRIVATE_KEY,
                "client_email": CLIENT_EMAIL,
            })
            firebase_admin.initialize_app(cred)
        print("Firebase Admin successfully initialized for auth token verification.")
    except Exception as e:
        print(f"ERROR: Failed to initialize Firebase Admin: {e}")
else:
    print("WARNING: Firebase Admin credentials not configured. Auth verification will bypass to Mock User.")


