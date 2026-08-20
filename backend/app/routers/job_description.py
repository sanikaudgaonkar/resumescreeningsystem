"""
JOB DESCRIPTION UPLOAD
Accepts PDF, DOCX, or TXT job descriptions
and extracts their text.
"""

import os
import uuid

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import settings
from app.services.text_extraction import extract_text


router = APIRouter(
    prefix="/api/job-description",
    tags=["job-description"]
)


@router.post("/upload")
async def upload_job_description(
    file: UploadFile = File(...)
):
    # Get extension
    ext = os.path.splitext(file.filename)[1].lower()

    # Supported formats
    if ext not in (".pdf", ".docx", ".txt"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF, DOCX, and TXT files are supported."
        )

    # Create unique ID
    job_description_id = str(uuid.uuid4())

    # Make sure upload directory exists
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)

    # Save file
    file_path = os.path.join(
        settings.UPLOAD_DIR,
        f"jd_{job_description_id}{ext}"
    )

    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Extract text
    if ext == ".txt":
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
        except UnicodeDecodeError:
            raise HTTPException(
                status_code=422,
                detail="Could not read the TXT file."
            )
    else:
        raw_text = extract_text(file_path)

    # Check extraction
    if not raw_text.strip():
        raise HTTPException(
            status_code=422,
            detail=(
                "Could not extract any text from this file. "
                "It may be a scanned/image-based PDF."
            )
        )

    return {
        "job_description_id": job_description_id,
        "filename": file.filename,
        "text": raw_text.strip(),
        "message": "Job description processed successfully."
    }