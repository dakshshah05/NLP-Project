import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
import cloudinary
import cloudinary.uploader
from sqlalchemy.orm import Session
from backend.app.database import get_db
from backend.app.models import Memory
from backend.app.security import get_current_user
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
def upload_file(
    file: UploadFile = File(...),
    user: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
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
        # Upload using file buffer
        upload_result = cloudinary.uploader.upload(
            file.file,
            resource_type="auto",
            folder="aura_ai_workspace"
        )
        secure_url = upload_result.get("secure_url")

        # Persist upload event directly to SQL 'memories' table to index search
        uid = user["uid"]
        new_mem = Memory(
            user_id=uid,
            category="documents",
            content=f"File: {file.filename} uploaded to cloud storage. Accessible at: {secure_url}"
        )
        db.add(new_mem)
        db.commit()

        return {
            "filename": file.filename,
            "url": secure_url,
            "format": upload_result.get("format"),
            "bytes": upload_result.get("bytes")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cloudinary upload crashed: {str(e)}")

