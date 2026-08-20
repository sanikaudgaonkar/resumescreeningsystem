from pydantic import BaseModel
from typing import List, Optional


class UploadResponse(BaseModel):
    resume_id: str
    filename: str
    chunks_indexed: int
    message: str


class ExtractedInfo(BaseModel):
    skills: List[str] = []
    education: List[str] = []
    experience_years: Optional[float] = None


class SentimentResult(BaseModel):
    tone: str                    # "confident" | "neutral" | "passive"
    confidence_score: float      # 0-1, based on action-verb density
    professionalism_score: float # 0-1, based on resume-writing conventions


class RequirementMatch(BaseModel):
    requirement: str
    evidence: Optional[str] = None
    score: float


class MatchScore(BaseModel):
    overall_score: float
    semantic_similarity: float
    matched_requirements: List[str] = []
    missing_requirements: List[str] = []
    requirement_matches: List[RequirementMatch] = []


class AnalysisRequest(BaseModel):
    resume_id: str
    job_description: str


class AnalysisResponse(BaseModel):
    resume_id: str
    extracted_info: ExtractedInfo
    sentiment: SentimentResult
    match_score: MatchScore
    llm_feedback: str
    summary: str