"""
STAGE 6: STORE IN VECTOR DB

ChromaDB stores resume chunks as embeddings.

The search layer retrieves multiple relevant resume chunks
for each JD requirement instead of relying on only one chunk.
"""

import chromadb

from app.config import settings


# ============================================================
# CHROMADB
# ============================================================

_client = chromadb.PersistentClient(
    path=settings.CHROMA_PERSIST_DIR
)

_collection = _client.get_or_create_collection(
    name="resume_chunks",
    metadata={
        "hnsw:space": "cosine"
    },
)


# ============================================================
# STORE RESUME CHUNKS
# ============================================================

def store_resume_chunks(
    resume_id: str,
    chunks: list[str],
    embeddings: list[list[float]],
    filename: str,
):
    """
    Store resume chunks and their embeddings.
    """

    if not chunks:
        return

    ids = [
        f"{resume_id}::chunk::{i}"
        for i in range(len(chunks))
    ]

    metadatas = [
        {
            "resume_id": resume_id,
            "filename": filename,
            "chunk_index": i,
        }
        for i in range(len(chunks))
    ]

    _collection.upsert(
        ids=ids,
        embeddings=embeddings,
        metadatas=metadatas,
        documents=chunks,
    )


# ============================================================
# QUERY TOP RESUME EVIDENCE
# ============================================================

def query_best_chunk_for_requirement(
    resume_id: str,
    requirement_embedding: list[float],
) -> dict | None:
    """
    Find the most relevant resume evidence for a JD requirement.

    Retrieves the top 3 chunks instead of only one.

    The strongest chunk remains the primary score so we don't
    artificially inflate the similarity percentage.
    """

    result = _collection.query(
        query_embeddings=[requirement_embedding],

        # Retrieve multiple pieces of evidence
        n_results=3,

        where={
            "resume_id": resume_id
        },
    )

    if (
        not result["ids"]
        or not result["ids"][0]
    ):
        return None

    distances = result["distances"][0]
    documents = result["documents"][0]

    evidence = []

    for distance, document in zip(
        distances,
        documents
    ):

        # Chroma cosine distance:
        #
        # distance = 1 - cosine_similarity
        #
        # Therefore:
        #
        # similarity = 1 - distance

        similarity = 1 - distance

        # Keep score between 0 and 1
        similarity = max(
            0.0,
            min(1.0, similarity)
        )

        evidence.append({
            "score": similarity,
            "chunk_text": document,
        })

    # Chroma already returns results from best
    # to worst similarity.
    best = evidence[0]

    return {
        "score": best["score"],
        "chunk_text": best["chunk_text"],

        # Keep all evidence available for the
        # next stage of the matching engine.
        "evidence": evidence,
    }


# ============================================================
# DELETE RESUME
# ============================================================

def delete_resume_chunks(
    resume_id: str
):
    """
    Delete all vector chunks belonging to a resume.
    """

    _collection.delete(
        where={
            "resume_id": resume_id
        }
    )
    