"""
Cross-encoder re-ranking. The bi-encoder retrieves a shortlist of
candidate resume chunks quickly. This cross-encoder scores each
(requirement, chunk) pair TOGETHER in one pass — far more accurate than
comparing independently-computed embeddings, at the cost of being too
slow to run against every chunk in a large corpus.
"""
from sentence_transformers import CrossEncoder
from app.config import settings
import numpy as np

_reranker = CrossEncoder(settings.RERANKER_MODEL)


def _sigmoid(x: float) -> float:
    return 1 / (1 + np.exp(-x))


def rerank(requirement_text: str, candidate_chunks: list[str]) -> list[dict]:
    if not candidate_chunks:
        return []

    pairs = [(requirement_text, chunk) for chunk in candidate_chunks]
    raw_scores = _reranker.predict(pairs)

    scored = [
        {"chunk": chunk, "score": float(_sigmoid(score))}
        for chunk, score in zip(candidate_chunks, raw_scores)
    ]
    scored.sort(key=lambda x: x["score"], reverse=True)
    return scored