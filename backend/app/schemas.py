from pydantic import BaseModel, Field
from typing import List, Optional


# ============================================================
# RESUME UPLOAD
# ============================================================

class UploadResponse(BaseModel):

    resume_id: str

    filename: str

    chunks_indexed: int

    message: str


# ============================================================
# EXTRACTED RESUME INFORMATION
# ============================================================

class ExtractedInfo(BaseModel):

    skills: List[str] = Field(
        default_factory=list
    )

    education: List[str] = Field(
        default_factory=list
    )

    experience_years: Optional[float] = None


# ============================================================
# SENTIMENT
# ============================================================

class SentimentResult(BaseModel):

    tone: str

    confidence_score: float

    professionalism_score: float


# ============================================================
# REQUIREMENT MATCH
# ============================================================

class RequirementMatch(BaseModel):

    requirement: str

    evidence: Optional[str] = None

    supporting_evidence: List[str] = Field(
        default_factory=list
    )

    score: float

    raw_similarity: Optional[float] = None

    category: Optional[str] = None

    weight: Optional[float] = None


# ============================================================
# MATCH SCORE
# ============================================================

class MatchScore(BaseModel):

    # Final combined score
    overall_score: float

    # Semantic component
    semantic_similarity: float

    # Additional scoring components
    skill_score: Optional[float] = None

    experience_score: Optional[float] = None

    education_score: Optional[float] = None

    # Requirement breakdown
    matched_requirements: List[str] = Field(
        default_factory=list
    )

    missing_requirements: List[str] = Field(
        default_factory=list
    )

    requirement_matches: List[
        RequirementMatch
    ] = Field(
        default_factory=list
    )


# ============================================================
# ANALYSIS REQUEST
# ============================================================

class AnalysisRequest(BaseModel):

    resume_id: str

    job_description: str


# ============================================================
# ANALYSIS RESPONSE
# ============================================================

class AnalysisResponse(BaseModel):

    resume_id: str

    extracted_info: ExtractedInfo

    sentiment: SentimentResult

    match_score: MatchScore

    llm_feedback: str

    summary: str