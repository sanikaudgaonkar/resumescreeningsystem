"""
STAGES 7-12 ORCHESTRATION

Coordinates:
1. Resume retrieval
2. Semantic requirement matching
3. Structured skill matching
4. Experience matching
5. Sentiment analysis
6. LLM feedback
7. Final report generation
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.schemas import AnalysisRequest, AnalysisResponse

from app.services.sentiment_analysis import analyze_sentiment
from app.services.skill_matching import compute_match_score
from app.services.semantic_matching import match_resume_to_requirements
from app.services.llm_feedback import generate_feedback
from app.services.report_generator import build_report

from app.database.db import get_db
from app.database.models import Resume


router = APIRouter(
    prefix="/api/analysis",
    tags=["analysis"],
)


@router.post(
    "/",
    response_model=AnalysisResponse
)
async def analyze_resume(
    request: AnalysisRequest,
    db: Session = Depends(get_db),
):

    # ========================================================
    # 1. Get resume
    # ========================================================

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == request.resume_id
        )
        .first()
    )

    if not resume:
        raise HTTPException(
            404,
            "Resume not found."
        )

    # ========================================================
    # 2. Semantic requirement matching
    # ========================================================

    semantic_result = match_resume_to_requirements(
        request.resume_id,
        request.job_description,
    )

    # ========================================================
    # 3. Extracted resume information
    # ========================================================

    extracted_info = {
        "skills": resume.skills or [],
        "education": resume.education or [],
        "experience_years": resume.experience_years,
    }

    # ========================================================
    # 4. Sentiment analysis
    # ========================================================

    sentiment = analyze_sentiment(
        resume.raw_text
    )

    # ========================================================
    # 5. Hybrid match score
    # ========================================================

    match_score = compute_match_score(

        semantic_similarity=(
            semantic_result["semantic_similarity"]
        ),

        requirement_matches=(
            semantic_result["requirement_matches"]
        ),

        resume_skills=(
            resume.skills or []
        ),

        resume_experience_years=(
            resume.experience_years
        ),

        job_description=(
            request.job_description
        ),
    )

    # ========================================================
    # 6. Generate LLM feedback
    # ========================================================

    feedback = generate_feedback(
        match_score,
        sentiment,
        request.job_description,
    )

    # ========================================================
    # 7. Build final report
    # ========================================================

    return build_report(
        resume_id=request.resume_id,
        extracted_info=extracted_info,
        sentiment=sentiment,
        match_score=match_score,
        llm_feedback=feedback,
    )