"""
STAGES 7-12 orchestration.
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import AnalysisRequest, AnalysisResponse
from app.services.sentiment_analysis import analyze_sentiment
from app.services.skill_matching import compute_match_score
from app.services.semantic_matching import match_resume_to_requirements
from app.services.gap_analyzer import analyze_gaps
from app.services.llm_feedback import generate_feedback
from app.services.report_generator import build_report
from app.database.db import get_db
from app.database.models import Resume

router = APIRouter(prefix="/api/analysis", tags=["analysis"])


@router.post("/", response_model=AnalysisResponse)
async def analyze_resume(request: AnalysisRequest, db: Session = Depends(get_db)):
    resume = db.query(Resume).filter(Resume.id == request.resume_id).first()
    if not resume:
        raise HTTPException(404, "Resume not found.")

    semantic_result = match_resume_to_requirements(request.resume_id, request.job_description)

    extracted_info = {
        "skills": resume.skills,
        "education": resume.education,
        "experience_years": resume.experience_years,
    }

    sentiment = analyze_sentiment(resume.raw_text)
    match_score = compute_match_score(
        semantic_similarity=semantic_result["semantic_similarity"],
        requirement_matches=semantic_result["requirement_matches"],
    )
    gap_analysis = analyze_gaps(semantic_result["requirement_matches"])
    feedback = generate_feedback(match_score, sentiment, request.job_description)

    return build_report(
        resume_id=request.resume_id,
        extracted_info=extracted_info,
        sentiment=sentiment,
        match_score=match_score,
        gap_analysis=gap_analysis,
        llm_feedback=feedback,
    )