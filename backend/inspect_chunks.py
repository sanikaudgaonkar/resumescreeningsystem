"""
One-off debug script: prints every chunk stored in ChromaDB for a given
resume_id, so you can see exactly what got indexed — run this from
inside backend/ with the venv active:

    python inspect_chunks.py 8f3c1df1-3527-4b49-b881-fb7fe38f1df3
"""
import sys
sys.path.insert(0, ".")
from app.services.vector_store import _collection

resume_id = sys.argv[1]

result = _collection.get(
    where={"resume_id": resume_id},
    include=["documents", "metadatas"],
)

chunks_with_index = list(zip(result["documents"], result["metadatas"]))
chunks_with_index.sort(key=lambda x: x[1]["chunk_index"])

print(f"Total chunks for {resume_id}: {len(chunks_with_index)}\n")
for doc, meta in chunks_with_index:
    print(f"[{meta['chunk_index']}] {doc}")