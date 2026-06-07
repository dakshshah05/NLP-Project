import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import cloudinary
import cloudinary.uploader
from backend.app.security import get_current_user
from backend.app.firebase_config import db_firestore
from datetime import datetime

router = APIRouter()

# Configure Cloudinary
cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

@router.post("/upload")
def upload_file(file: UploadFile = File(...), user: dict = Depends(get_current_user)):
    # Restrict to standard text, image, docx, pdf formats
    allowed_types = [
        "application/pdf", 
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 
        "image/png", 
        "image/jpeg", 
        "image/webp",
        "text/plain",
        "application/json"
    ]
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail=f"File type {file.content_type} not supported.")

    try:
        cloud_name = os.getenv("CLOUDINARY_CLOUD_NAME")
        if not cloud_name:
            # Local filesystem fallback
            os.makedirs("workspace", exist_ok=True)
            local_path = os.path.join("workspace", file.filename)
            file_content = file.file.read()
            with open(local_path, "wb") as f:
                f.write(file_content)
            
            secure_url = f"/workspace/{file.filename}"
            file_format = file.filename.split(".")[-1] if "." in file.filename else "bin"
            file_size = len(file_content)

            uid = user["uid"]
            mem_ref = db_firestore.collection("memories").document()
            mem_data = {
                "userId": uid,
                "category": "documents",
                "content": f"File: {file.filename} saved to local workspace. Path: {secure_url}",
                "created_at": datetime.utcnow().isoformat()
            }
            mem_ref.set(mem_data)

            return {
                "filename": file.filename,
                "url": secure_url,
                "format": file_format,
                "bytes": file_size
            }

        # Upload using Cloudinary API
        upload_result = cloudinary.uploader.upload(
            file.file,
            resource_type="auto",
            folder="aura_ai_workspace"
        )
        secure_url = upload_result.get("secure_url")

        # Persist upload event directly to Firestore 'memories' collection to index search
        uid = user["uid"]
        mem_ref = db_firestore.collection("memories").document()
        mem_data = {
            "userId": uid,
            "category": "documents",
            "content": f"File: {file.filename} uploaded to cloud storage. Accessible at: {secure_url}",
            "created_at": datetime.utcnow().isoformat()
        }
        mem_ref.set(mem_data)

        return {
            "filename": file.filename,
            "url": secure_url,
            "format": upload_result.get("format"),
            "bytes": upload_result.get("bytes")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Storage upload crashed: {str(e)}")

