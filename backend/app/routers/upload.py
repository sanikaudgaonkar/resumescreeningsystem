"""
STAGE 1: UPLOAD RESUME
"""
import uuid
import os
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.schemas import UploadResponse
from app.services.text_extraction import extract_text
from app.services.preprocessing import preprocess
from app.services.information_extraction import extract_information
from app.services.chunking import chunk_resume
from app.services.embedding import generate_embeddings_batch
from app.services.vector_store import store_resume_chunks
from app.database.db import get_db
from app.database.models import Resume

router = APIRouter(prefix="/api/resumes", tags=["resumes"])


@router.post("/upload", response_model=UploadResponse)
async def upload_resume(file: UploadFile = File(...), db: Session = Depends(get_db)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in (".pdf", ".docx"):
        raise HTTPException(400, "Only PDF and DOCX files are supported.")

    resume_id = str(uuid.uuid4())
    os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
    file_path = os.path.join(settings.UPLOAD_DIR, f"{resume_id}{ext}")

    with open(file_path, "wb") as f:
        f.write(await file.read())

    raw_text = extract_text(file_path)
    if not raw_text.strip():
        raise HTTPException(422, "Could not extract any text from this file. It may be a scanned/image-based PDF.")

    processed = preprocess(raw_text)
    info = extract_information(processed["cleaned_text"])

    chunks = chunk_resume(processed["cleaned_text"])
    if chunks:
        chunk_embeddings = generate_embeddings_batch(chunks)
        store_resume_chunks(resume_id, chunks, chunk_embeddings, file.filename)

    db_resume = Resume(
        id=resume_id,
        filename=file.filename,
        raw_text=raw_text,
        skills=info["skills"],
        education=info["education"],
        experience_years=info["experience_years"],
    )
    db.add(db_resume)
    db.commit()

    return UploadResponse(
        resume_id=resume_id,
        filename=file.filename,
        chunks_indexed=len(chunks),
        message=f"Resume processed successfully ({len(chunks)} sections indexed for semantic search).",
    )