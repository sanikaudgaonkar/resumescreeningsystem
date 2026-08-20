from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.database.models import Resume

router = APIRouter(prefix="/api/dashboard", tags=["dashboard"])


@router.get("/resumes")
async def list_resumes(db: Session = Depends(get_db)):
    resumes = db.query(Resume).all()
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "skills": r.skills,
            "experience_years": r.experience_years,
            "uploaded_at": r.uploaded_at,
        }
        for r in resumes
    ]