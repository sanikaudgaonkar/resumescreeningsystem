"""
STAGE 5: EMBEDDING GENERATION
Uses BAAI/bge-small-en-v1.5 — a retrieval-optimized embedding model that
distinguishes between "queries" (short search intents) and "passages"
(the documents being searched). JD requirements are queries; resume
chunks are passages. BGE recommends prefixing QUERIES ONLY with an
instruction string — this measurably improves retrieval accuracy versus
treating both sides symmetrically, which is what a generic sentence
similarity model (like the previous MiniLM-L6-v2) does.
"""
from sentence_transformers import SentenceTransformer
from app.config import settings

_model = SentenceTransformer(settings.EMBEDDING_MODEL)

_QUERY_INSTRUCTION = "Represent this sentence for searching relevant passages: "


def generate_passage_embedding(text: str) -> list[float]:
    return _model.encode(text, normalize_embeddings=True).tolist()


def generate_passage_embeddings_batch(texts: list[str]) -> list[list[float]]:
    return _model.encode(texts, normalize_embeddings=True).tolist()


def generate_query_embedding(text: str) -> list[float]:
    return _model.encode(_QUERY_INSTRUCTION + text, normalize_embeddings=True).tolist()


def generate_query_embeddings_batch(texts: list[str]) -> list[list[float]]:
    prefixed = [_QUERY_INSTRUCTION + t for t in texts]
    return _model.encode(prefixed, normalize_embeddings=True).tolist()


def generate_embedding(text: str) -> list[float]:
    return generate_passage_embedding(text)


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    return generate_passage_embeddings_batch(texts)
