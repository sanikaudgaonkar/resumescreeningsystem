"""
STAGE 6: STORE IN VECTOR DB (ChromaDB — local, free, no signup)
Stores resumes as chunk-level embeddings, one per bullet/line, so
semantic matching can find specific evidence per JD requirement.
"""
import chromadb
from app.config import settings

_client = chromadb.PersistentClient(path=settings.CHROMA_PERSIST_DIR)
_collection = _client.get_or_create_collection(
    name="resume_chunks",
    metadata={"hnsw:space": "cosine"},
)


def store_resume_chunks(resume_id: str, chunks: list[str], embeddings: list[list[float]], filename: str):
    if not chunks:
        return
    ids = [f"{resume_id}::chunk::{i}" for i in range(len(chunks))]
    metadatas = [{"resume_id": resume_id, "filename": filename, "chunk_index": i} for i in range(len(chunks))]
    _collection.upsert(ids=ids, embeddings=embeddings, metadatas=metadatas, documents=chunks)


def query_best_chunk_for_requirement(resume_id: str, requirement_embedding: list[float]) -> dict | None:
    result = _collection.query(
        query_embeddings=[requirement_embedding],
        n_results=1,
        where={"resume_id": resume_id},
    )
    if not result["ids"] or not result["ids"][0]:
        return None
    distance = result["distances"][0][0]
    similarity = max(0.0, 1 - distance)  # cosine space: distance = 1 - similarity
    return {"score": similarity, "chunk_text": result["documents"][0][0]}


def delete_resume_chunks(resume_id: str):
    _collection.delete(where={"resume_id": resume_id})