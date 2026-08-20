"""
STAGE 9/10: SCORING
Fully semantic. No keyword list, no alias maintenance. A requirement is
"matched" if the vector search found strong evidence for it in the resume
(above NO_EVIDENCE_THRESHOLD in semantic_matching.py), "missing" if not.
overall_score IS the semantic similarity — nothing else feeds it.
"""


def compute_match_score(
    semantic_similarity: float,
    requirement_matches: list[dict],
) -> dict:
    matched = [r["requirement"] for r in requirement_matches if r["evidence"]]
    missing = [r["requirement"] for r in requirement_matches if not r["evidence"]]

    return {
        "overall_score": round(semantic_similarity, 2),
        "semantic_similarity": round(semantic_similarity, 2),
        "matched_requirements": matched,
        "missing_requirements": missing,
        "requirement_matches": requirement_matches,
    }