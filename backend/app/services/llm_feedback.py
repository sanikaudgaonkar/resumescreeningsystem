"""
STAGE 11: LLM ANALYSIS & FEEDBACK
Deliberately constrained: the LLM's job is ONLY to write a short recruiter
takeaway from data that's already been computed (semantic scores, matched/
missing requirements). It is explicitly instructed not to re-describe the
resume's contents, not to list every match, and to stay within a strict
length budget — otherwise it tends to just narrate the whole resume back,
which adds no value over reading the requirement table directly.
"""
import google.generativeai as genai
from app.config import settings

genai.configure(api_key=settings.GEMINI_API_KEY)
_model = genai.GenerativeModel("gemini-3.6-flash")


def generate_feedback(match_score: dict, sentiment: dict, job_description: str) -> str:
    matched = match_score.get("matched_requirements", [])
    missing = match_score.get("missing_requirements", [])
    score = match_score.get("overall_score", 0.0)

    matched_preview = matched[:3]
    missing_preview = missing[:3]

    prompt = f"""You are a recruiter writing a brief internal note about a candidate.
You are NOT summarizing the resume — the reader has already seen the resume
and a detailed requirement-match table. Your only job is a short verdict.

Overall semantic match score: {score * 100:.0f}%
Strongest matched requirements: {matched_preview if matched_preview else "none"}
Notable gaps: {missing_preview if missing_preview else "none"}
Resume tone: {sentiment.get('tone')}

Write EXACTLY 3 sentences, in this order:
1. One sentence verdict (strong fit / moderate fit / weak fit) with the single
   biggest reason why, referencing at most one matched requirement in your own words.
2. One sentence on the single most important gap, in your own words.
3. One sentence recommendation (proceed to interview / consider with reservations /
   likely not a fit for this specific role).

Do not quote the resume. Do not list multiple skills. Do not restate the job
description. Do not use bullet points. Plain prose, 3 sentences only, nothing else."""

    response = _model.generate_content(prompt)
    return response.text.strip()