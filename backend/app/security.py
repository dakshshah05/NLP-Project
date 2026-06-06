import os
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from firebase_admin import auth

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    
    # Check if Firebase credentials are set and initialized. If not, bypass to mock user for local devs.
    if not os.getenv("FIREBASE_PROJECT_ID") or not firebase_admin._apps:
        return {
            "uid": "dev_mock_user_99",
            "email": "dev-user@aura.ai",
            "name": "Developer Mock User"
        }

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
