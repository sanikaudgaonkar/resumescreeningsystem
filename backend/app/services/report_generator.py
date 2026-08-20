"""
STAGE 12: GENERATE FINAL REPORT
"""
from app.schemas import AnalysisResponse, ExtractedInfo, SentimentResult, MatchScore


def build_report(resume_id, extracted_info, sentiment, match_score, llm_feedback) -> AnalysisResponse:
    summary = (
        f"Semantic match: {match_score['overall_score']*100:.0f}%. "
        f"{len(match_score['matched_requirements'])} requirements matched, "
        f"{len(match_score['missing_requirements'])} gaps identified."
    )
    return AnalysisResponse(
        resume_id=resume_id,
        extracted_info=ExtractedInfo(**extracted_info),
        sentiment=SentimentResult(**sentiment),
        match_score=MatchScore(**match_score),
        llm_feedback=llm_feedback,
        summary=summary,
    )