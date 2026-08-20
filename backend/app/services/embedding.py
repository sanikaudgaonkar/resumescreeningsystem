"""
STAGE 5: EMBEDDING GENERATION
"""
from sentence_transformers import SentenceTransformer
from app.config import settings

_model = SentenceTransformer(settings.EMBEDDING_MODEL)


def generate_embedding(text: str) -> list[float]:
    return _model.encode(text, normalize_embeddings=True).tolist()


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    return _model.encode(texts, normalize_embeddings=True).tolist()