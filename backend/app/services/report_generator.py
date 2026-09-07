"""
STAGE 12: GENERATE FINAL REPORT
"""
from app.schemas import (
    AnalysisResponse, ExtractedInfo, SentimentResult, MatchScore, GapAnalysis
)


def build_report(resume_id, extracted_info, sentiment, match_score, gap_analysis, llm_feedback) -> AnalysisResponse:
    summary = (
        f"Semantic match: {match_score['overall_score']*100:.0f}%. "
        f"{gap_analysis['summary']['critical_gaps']} critical gaps, "
        f"{gap_analysis['summary']['total_matched']} requirements matched."
    )
    return AnalysisResponse(
        resume_id=resume_id,
        extracted_info=ExtractedInfo(**extracted_info),
        sentiment=SentimentResult(**sentiment),
        match_score=MatchScore(**match_score),
        gap_analysis=GapAnalysis(**gap_analysis),
        llm_feedback=llm_feedback,
        summary=summary,
    )