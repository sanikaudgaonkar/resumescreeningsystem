"""
STAGES 7-10: SEMANTIC REQUIREMENT MATCHING

Matches each JD requirement against multiple pieces of resume
evidence using semantic similarity.

Improvements:
- Retrieves top 3 resume evidence chunks
- Uses multiple evidence pieces instead of only one
- Applies a semantic calibration curve
- Gives more importance to strong evidence
- Keeps requirement-level scores explainable
"""

import math
import re
from app.services.chunking import chunk_job_description
from app.services.embedding import generate_embeddings_batch
from app.services.vector_store import (
    query_best_chunk_for_requirement,
)


# ============================================================
# CONFIGURATION
# ============================================================

# Below this, evidence is considered too weak to display.
NO_EVIDENCE_THRESHOLD = 0.50

# Similarity at which the calibration curve is approximately
# a 50% match.
CALIBRATION_CENTER = 0.45

# Controls how quickly similarity increases around the center.
CALIBRATION_STEEPNESS = 8.0


# ============================================================
# SEMANTIC SCORE CALIBRATION
# ============================================================

def calibrate_similarity(raw_score: float) -> float:
    """
    Convert raw cosine similarity into a more useful
    match score.

    IMPORTANT:
    Raw cosine similarity should NOT simply be multiplied
    by 100 and presented as candidate suitability.

    Example:
        raw 0.30 -> low match
        raw 0.45 -> moderate match
        raw 0.60 -> strong match
        raw 0.75 -> very strong match
    """

    raw_score = max(
        0.0,
        min(1.0, raw_score)
    )

    calibrated = 1 / (
        1 + math.exp(
            -CALIBRATION_STEEPNESS
            * (raw_score - CALIBRATION_CENTER)
        )
    )

    return max(
        0.0,
        min(1.0, calibrated)
    )


# ============================================================
# MULTIPLE EVIDENCE SCORING
# ============================================================

def calculate_evidence_score(
    evidence: list[dict]
) -> float:
    """
    Calculate a score using the top resume evidence.

    The strongest evidence gets the most weight.

    Weights:
        Top 1 = 70%
        Top 2 = 20%
        Top 3 = 10%

    Weak supporting evidence is ignored.
    """

    if not evidence:
        return 0.0

    valid_scores = []

    for item in evidence:

        score = item.get(
            "score",
            0.0
        )

        if score >= NO_EVIDENCE_THRESHOLD:
            valid_scores.append(score)

    if not valid_scores:
        return 0.0

    # Chroma returns evidence in descending order.
    top1 = valid_scores[0]

    top2 = (
        valid_scores[1]
        if len(valid_scores) > 1
        else 0.0
    )

    top3 = (
        valid_scores[2]
        if len(valid_scores) > 2
        else 0.0
    )

    # Only give supporting evidence weight when
    # it actually exists.
    if len(valid_scores) == 1:

        combined = top1

    elif len(valid_scores) == 2:

        combined = (
            top1 * 0.75
            + top2 * 0.25
        )

    else:

        combined = (
            top1 * 0.70
            + top2 * 0.20
            + top3 * 0.10
        )

    return max(
        0.0,
        min(1.0, combined)
    )


# ============================================================
# REQUIREMENT CLASSIFICATION
# ============================================================

def classify_requirement(
    requirement: str
) -> str:
    """
    Classify requirements into broad categories.

    This is used only for transparency and future
    weighting improvements.
    """

    text = requirement.lower()

    experience_terms = [
        "years of experience",
        "months of experience",
        "internship experience",
        "prior experience",
        "relevant experience",
        "experience in",
    ]

    education_terms = [
        "bachelor",
        "master",
        "degree",
        "graduate",
        "graduation",
        "education",
    ]

    portfolio_terms = [
        "portfolio",
        "projects",
        "case study",
    ]

    skill_terms = [
        "figma",
        "photoshop",
        "illustrator",
        "html",
        "css",
        "javascript",
        "react",
        "python",
        "sql",
        "wireframe",
        "wireframing",
        "prototype",
        "prototyping",
        "ux research",
        "user research",
        "interaction design",
        "responsive design",
        "design system",
    ]

    if any(
        term in text
        for term in experience_terms
    ):
        return "experience"

    if any(
        term in text
        for term in education_terms
    ):
        return "education"

    if any(
        term in text
        for term in portfolio_terms
    ):
        return "portfolio"

    if any(
        term in text
        for term in skill_terms
    ):
        return "skill"

    return "general"


# ============================================================
# REQUIREMENT WEIGHT
# ============================================================

def get_requirement_weight(
    requirement: str
) -> float:
    """
    Give slightly more importance to skills, experience
    and portfolio requirements.

    These weights affect the overall semantic score,
    not the individual requirement score.
    """

    category = classify_requirement(
        requirement
    )

    if category == "skill":
        return 1.15

    if category == "experience":
        return 1.20

    if category == "portfolio":
        return 1.15

    if category == "education":
        return 1.00

    return 1.00


# ============================================================
# MAIN MATCHING FUNCTION
# ============================================================

def match_resume_to_requirements(
    resume_id: str,
    job_description: str
) -> dict:

    # --------------------------------------------------------
    # 1. Extract individual JD requirements
    # --------------------------------------------------------

    requirements = chunk_job_description(
        job_description
    )

    if not requirements:

        return {
            "requirement_matches": [],
            "semantic_similarity": 0.0,
        }

    # --------------------------------------------------------
    # 2. Generate embeddings
    # --------------------------------------------------------

    requirement_embeddings = (
        generate_embeddings_batch(
            requirements
        )
    )

    requirement_matches = []

    weighted_score_total = 0.0
    total_weight = 0.0

    # --------------------------------------------------------
    # 3. Match every requirement
    # --------------------------------------------------------

    for (
        requirement_text,
        requirement_embedding,
    ) in zip(
        requirements,
        requirement_embeddings,
    ):

        result = query_best_chunk_for_requirement(
            resume_id,
            requirement_embedding,
        )

        # ----------------------------------------------------
        # No evidence found
        # ----------------------------------------------------

        if not result:

            requirement_matches.append({
                "requirement": requirement_text,
                "evidence": None,
                "score": 0.0,
                "category": classify_requirement(
                    requirement_text
                ),
            })

            continue

        # ----------------------------------------------------
        # Get top evidence
        # ----------------------------------------------------

        evidence_items = result.get(
            "evidence",
            [],
        )

        # Backwards compatibility with the old vector_store
        if not evidence_items:

            evidence_items = [{
                "score": result.get(
                    "score",
                    0.0
                ),
                "chunk_text": result.get(
                    "chunk_text",
                    "",
                ),
            }]

        # ----------------------------------------------------
        # Calculate combined raw similarity
        # ----------------------------------------------------

        raw_score = calculate_evidence_score(
            evidence_items
        )

        # ----------------------------------------------------
        # Convert raw similarity into calibrated score
        # ----------------------------------------------------

        calibrated_score = calibrate_similarity(
            raw_score
        )

        # ----------------------------------------------------
        # Primary evidence
        # ----------------------------------------------------

        primary_evidence = None

        if raw_score >= NO_EVIDENCE_THRESHOLD:

            primary_evidence = (
                evidence_items[0]
                .get("chunk_text")
            )

        # ----------------------------------------------------
        # Supporting evidence
        # ----------------------------------------------------

        supporting_evidence = []

        for item in evidence_items[1:]:

            if item.get("score", 0.0) >= (
                NO_EVIDENCE_THRESHOLD
            ):

                supporting_evidence.append(
                    item.get(
                        "chunk_text"
                    )
                )

        # ----------------------------------------------------
        # Requirement category
        # ----------------------------------------------------

        category = classify_requirement(
            requirement_text
        )

        weight = get_requirement_weight(
            requirement_text
        )

        # ----------------------------------------------------
        # Store result
        # ----------------------------------------------------

        requirement_matches.append({

            "requirement": requirement_text,

            "evidence": primary_evidence,

            "supporting_evidence": (
                supporting_evidence
            ),

            "score": round(
                calibrated_score,
                2,
            ),

            "raw_similarity": round(
                raw_score,
                2,
            ),

            "category": category,

            "weight": weight,
        })

        # ----------------------------------------------------
        # Weighted overall score
        # ----------------------------------------------------

        weighted_score_total += (
            calibrated_score * weight
        )

        total_weight += weight

    # ========================================================
    # 4. Overall score
    # ========================================================

    if total_weight > 0:

        semantic_similarity = (
            weighted_score_total
            / total_weight
        )

    else:

        semantic_similarity = 0.0

    semantic_similarity = max(
        0.0,
        min(1.0, semantic_similarity)
    )

    # ========================================================
    # 5. Return
    # ========================================================

    return {

        "requirement_matches":
            requirement_matches,

        "semantic_similarity":
            round(
                semantic_similarity,
                2,
            ),
    }

# ============================================================
# PORTFOLIO DETECTION
# ============================================================

PORTFOLIO_URL_PATTERNS = [
    "portfolio",
    "behance.net",
    "dribbble.com",
]


def is_portfolio_requirement(
    requirement: str,
) -> bool:

    text = requirement.lower()

    portfolio_terms = [
        "portfolio",
        "design portfolio",
        "ui/ux portfolio",
        "ux portfolio",
        "design work",
        "case studies",
        "case study",
    ]

    return any(
        term in text
        for term in portfolio_terms
    )


def detect_portfolio_link(
    resume_text: str,
) -> str | None:

    if not resume_text:
        return None

    urls = re.findall(
        r"https?://[^\s<>\"']+",
        resume_text,
        re.IGNORECASE,
    )

    for url in urls:

        url_lower = url.lower()

        if any(
            pattern in url_lower
            for pattern in PORTFOLIO_URL_PATTERNS
        ):

            return url

    return None