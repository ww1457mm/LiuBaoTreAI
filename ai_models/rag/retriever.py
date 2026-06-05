from __future__ import annotations

from typing import List

from ai_models.rag.vector_store import VectorStore

_store: VectorStore | None = None


def get_store() -> VectorStore:
    global _store
    if _store is None:
        _store = VectorStore()
        _store.build_if_needed()
    return _store


def retrieve(query: str, top_k: int = 3) -> List[dict]:
    results = get_store().search(query, top_k=top_k)
    return [
        {
            "title": chunk["title"],
            "content": chunk["content"],
            "source": chunk["source"],
            "category": chunk.get("category", ""),
            "score": round(score, 4),
        }
        for chunk, score in results
    ]
