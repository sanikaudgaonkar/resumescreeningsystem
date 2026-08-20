"""
STAGES 7-10 (core engine): SEMANTIC REQUIREMENT MATCHING
Breaks the JD into individual requirements and finds the best-matching
evidence for each inside the resume via vector search. This is the
primary — and only — scoring mechanism. No keyword layer involved.
"""
from app.services.chunking import chunk_job_description
from app.services.embedding import generate_embeddings_batch
from app.services.vector_store import query_best_chunk_for_requirement

# Below this, treat a requirement as "no real evidence" rather than a
# weak match. Tuned empirically for all-MiniLM-L6-v2 — raw cosine scores
# for genuinely related-but-differently-worded text typically land 0.25-0.6.
NO_EVIDENCE_THRESHOLD = 0.30


def match_resume_to_requirements(resume_id: str, job_description: str) -> dict:
    requirements = chunk_job_description(job_description)
    if not requirements:
        return {"requirement_matches": [], "semantic_similarity": 0.0}

    requirement_embeddings = generate_embeddings_batch(requirements)
    requirement_matches = []
    scores = []

    for requirement_text, requirement_embedding in zip(requirements, requirement_embeddings):
        result = query_best_chunk_for_requirement(resume_id, requirement_embedding)
        score = result["score"] if result else 0.0

        if result and score >= NO_EVIDENCE_THRESHOLD:
            requirement_matches.append({
                "requirement": requirement_text,
                "evidence": result["chunk_text"],
                "score": round(score, 2),
            })
        else:
            requirement_matches.append({
                "requirement": requirement_text,
                "evidence": None,
                "score": round(score, 2),
            })
        scores.append(score)

    semantic_similarity = sum(scores) / len(scores) if scores else 0.0
    return {
        "requirement_matches": requirement_matches,
        "semantic_similarity": round(semantic_similarity, 2),
    }