# app/routers/upload.py
import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime

from app.state import repos
from app.state.db import get_db
from app.services.storage_manager import StorageManager

router = APIRouter()

@router.post("/")
async def upload_document(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    """
    Uploads a file to Azure Blob Storage without requiring session_id.
    """
    storage_manager = StorageManager()

    # Unique blob name with timestamp
    timestamp = datetime.utcnow().strftime("%Y%m%d%H%M%S")
    blob_name = f"{timestamp}_{file.filename}"

    # Write file to temp
    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        temp_path = tmp_file.name
        tmp_file.write(await file.read())

    try:
        # Upload to Azure Blob
        storage_manager.upload_file(temp_path, blob_name)

        # Insert into DB without session
        doc = repos.create_document(
            db=db,
            session_id=None,
            filename=file.filename,
            blob_url=blob_name
        )

        return {
            "message": "File uploaded successfully",
            "blobPath": blob_name,
            "documentId": doc.id
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass
