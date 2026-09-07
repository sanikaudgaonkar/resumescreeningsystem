"""
STAGES 7-10 (core engine): SEMANTIC REQUIREMENT MATCHING
Two-stage retrieval: bi-encoder retrieves top-K candidates fast,
cross-encoder re-ranks them for accuracy.
"""
from app.services.chunking import chunk_job_description
from app.services.embedding import generate_query_embeddings_batch
from app.services.vector_store import query_top_k_chunks_for_requirement
from app.services.reranker import rerank

NO_EVIDENCE_THRESHOLD = 0.40
CANDIDATES_PER_REQUIREMENT = 5


def match_resume_to_requirements(resume_id: str, job_description: str) -> dict:
    requirements = chunk_job_description(job_description)
    if not requirements:
        return {"requirement_matches": [], "semantic_similarity": 0.0}

    requirement_embeddings = generate_query_embeddings_batch(requirements)
    requirement_matches = []
    scores = []

    for requirement_text, requirement_embedding in zip(requirements, requirement_embeddings):
        candidates = query_top_k_chunks_for_requirement(
            resume_id, requirement_embedding, k=CANDIDATES_PER_REQUIREMENT
        )
        candidate_texts = [c["chunk_text"] for c in candidates]
        reranked = rerank(requirement_text, candidate_texts)

        top_score = reranked[0]["score"] if reranked else 0.0

        if reranked and top_score >= NO_EVIDENCE_THRESHOLD:
            requirement_matches.append({
                "requirement": requirement_text,
                "evidence": reranked[0]["chunk"],
                "score": round(top_score, 2),
            })
        else:
            requirement_matches.append({
                "requirement": requirement_text,
                "evidence": None,
                "score": round(top_score, 2),
            })
        scores.append(top_score)

    semantic_similarity = sum(scores) / len(scores) if scores else 0.0
    return {
        "requirement_matches": requirement_matches,
        "semantic_similarity": round(semantic_similarity, 2),
    }