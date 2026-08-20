"""
STAGE 11: LLM ANALYSIS & FEEDBACK

The LLM is ONLY responsible for generating a short recruiter
takeaway from already-computed matching data.

The actual match score is calculated by the matching engine,
not by Gemini.

If Gemini is unavailable or quota is exceeded, a fallback
feedback message is returned so the analysis can still succeed.
"""

import google.generativeai as genai

from app.config import settings


# ============================================================
# GEMINI CONFIGURATION
# ============================================================

genai.configure(
    api_key=settings.GEMINI_API_KEY
)

_model = genai.GenerativeModel(
    "gemini-3.6-flash"
)


# ============================================================
# FALLBACK FEEDBACK
# ============================================================

def generate_fallback_feedback(match_score: dict) -> str:
    """
    Generates recruiter feedback without Gemini.

    This is used when:
    - Gemini quota is exceeded
    - Gemini API is unavailable
    - Gemini returns an empty response
    - Any unexpected Gemini error occurs
    """

    score = (
        match_score.get(
            "overall_score",
            0.0
        ) * 100
    )

    matched = match_score.get(
        "matched_requirements",
        []
    )

    missing = match_score.get(
        "missing_requirements",
        []
    )

    # --------------------------------------------------------
    # Verdict
    # --------------------------------------------------------

    if score >= 80:

        verdict = (
            "This candidate is a strong fit for the role"
        )

        recommendation = (
            "The candidate should be considered for an interview."
        )

    elif score >= 60:

        verdict = (
            "This candidate is a moderate fit for the role"
        )

        recommendation = (
            "The candidate can be considered with some reservations."
        )

    elif score >= 40:

        verdict = (
            "This candidate shows partial alignment with the role"
        )

        recommendation = (
            "The candidate should be reviewed carefully against the key requirements."
        )

    else:

        verdict = (
            "This candidate shows limited alignment with the role"
        )

        recommendation = (
            "The candidate is unlikely to be a strong fit for this specific role."
        )

    # --------------------------------------------------------
    # Main strength
    # --------------------------------------------------------

    if matched:

        strongest_match = matched[0]

        strength = (
            f"The strongest evidence is related to "
            f"{strongest_match.lower()}."
        )

    else:

        strength = (
            "Limited supporting evidence was found in the resume."
        )

    # --------------------------------------------------------
    # Main gap
    # --------------------------------------------------------

    if missing:

        biggest_gap = missing[0]

        gap = (
            f"The main gap is the lack of clear evidence for "
            f"{biggest_gap.lower()}."
        )

    else:

        gap = (
            "No major requirement gaps were identified."
        )

    return (
        f"{verdict}. "
        f"{strength} "
        f"{gap} "
        f"{recommendation}"
    )


# ============================================================
# GEMINI FEEDBACK
# ============================================================

def generate_feedback(
    match_score: dict,
    sentiment: dict,
    job_description: str,
) -> str:

    matched = match_score.get(
        "matched_requirements",
        []
    )

    missing = match_score.get(
        "missing_requirements",
        []
    )

    score = match_score.get(
        "overall_score",
        0.0
    )

    # --------------------------------------------------------
    # Only send a small amount of information to Gemini
    # --------------------------------------------------------

    matched_preview = matched[:3]
    missing_preview = missing[:3]

    prompt = f"""
You are a recruiter writing a brief internal note about a candidate.

You are NOT summarizing the resume.

The reader has already seen the detailed requirement-match
table.

Your only job is to provide a short recruiter verdict.

Overall match score:
{score * 100:.0f}%

Strongest matched requirements:
{matched_preview if matched_preview else "None"}

Notable gaps:
{missing_preview if missing_preview else "None"}

Resume tone:
{sentiment.get("tone", "neutral")}

Write EXACTLY 3 sentences.

Sentence 1:
Give a verdict (strong fit, moderate fit, or weak fit)
and mention the single biggest reason.

Sentence 2:
Mention the single most important gap.

Sentence 3:
Give a recommendation:
proceed to interview,
consider with reservations,
or likely not a fit.

Rules:
- Do not summarize the resume.
- Do not list multiple skills.
- Do not restate the job description.
- Do not invent information.
- Do not quote the resume.
- Do not use bullet points.
- Exactly 3 sentences.
- Plain prose only.
"""

    # ========================================================
    # CALL GEMINI SAFELY
    # ========================================================

    try:

        response = _model.generate_content(
            prompt
        )

        # ----------------------------------------------------
        # Validate response
        # ----------------------------------------------------

        if response and response.text:

            return response.text.strip()

        print(
            "WARNING: Gemini returned an empty response. "
            "Using fallback feedback."
        )

        return generate_fallback_feedback(
            match_score
        )

    # ========================================================
    # QUOTA / API ERROR
    # ========================================================

    except Exception as e:

        print(
            "\nWARNING: Gemini feedback unavailable."
        )

        print(
            f"Reason: {e}"
        )

        print(
            "Using fallback recruiter feedback instead.\n"
        )

        return generate_fallback_feedback(
            match_score
        )