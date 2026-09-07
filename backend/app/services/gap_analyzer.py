"""
STAGE 10 (extended): GAP ANALYSIS & PRIORITIZED ROADMAP
Combines the semantic match/no-match verdict for each requirement (from
semantic_matching.py) with an urgency tier (derived from how the
requirement is phrased in the JD) to produce a structured gap breakdown
and a 3-tier improvement roadmap — similar to how a recruiter would
triage which gaps matter most.
"""
from app.services.chunking import classify_urgency

TIER_ORDER = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}


def analyze_gaps(requirement_matches: list[dict]) -> dict:
    tiered = []
    for r in requirement_matches:
        urgency = classify_urgency(r["requirement"])
        status = "matched" if r["evidence"] else "missing"
        tiered.append({
            "requirement": r["requirement"],
            "status": status,
            "urgency": urgency,
            "score": r["score"],
            "evidence": r["evidence"],
        })

    missing = [t for t in tiered if t["status"] == "missing"]
    missing.sort(key=lambda t: TIER_ORDER[t["urgency"]])

    roadmap = {
        "immediate": [t["requirement"] for t in missing if t["urgency"] == "CRITICAL"],
        "next": [t["requirement"] for t in missing if t["urgency"] in ("HIGH", "MEDIUM")],
        "optional": [t["requirement"] for t in missing if t["urgency"] == "LOW"],
    }

    summary = {
        "critical_gaps": sum(1 for t in missing if t["urgency"] == "CRITICAL"),
        "high_gaps": sum(1 for t in missing if t["urgency"] == "HIGH"),
        "medium_gaps": sum(1 for t in missing if t["urgency"] == "MEDIUM"),
        "low_gaps": sum(1 for t in missing if t["urgency"] == "LOW"),
        "total_matched": sum(1 for t in tiered if t["status"] == "matched"),
    }

    return {
        "requirement_breakdown": tiered,
        "roadmap": roadmap,
        "summary": summary,
    }