from __future__ import annotations

import json
import os
from pathlib import Path
from typing import List, Tuple

import numpy as np

from ai_models.rag.embedding import embed_texts

PROJECT_ROOT = Path(__file__).resolve().parents[2]
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge_base"
INDEX_DIR = PROJECT_ROOT / "ai_models" / "rag" / "index"
INDEX_PATH = INDEX_DIR / "faiss.index"
META_PATH = INDEX_DIR / "meta.json"


class VectorStore:
    def __init__(self):
        self.index = None
        self.chunks: List[dict] = []
        INDEX_DIR.mkdir(parents=True, exist_ok=True)

    def build_if_needed(self) -> None:
        if INDEX_PATH.exists() and META_PATH.exists():
            self._load()
            return
        self._build_from_knowledge_base()

    def _build_from_knowledge_base(self) -> None:
        chunks = []
        for txt in KNOWLEDGE_DIR.rglob("*.txt"):
            content = txt.read_text(encoding="utf-8").strip()
            if not content:
                continue
            category = txt.parent.name
            chunks.append(
                {
                    "title": txt.stem,
                    "content": content,
                    "source": str(txt.relative_to(PROJECT_ROOT)).replace("\\", "/"),
                    "category": category,
                }
            )
        if not chunks:
            return
        texts = [f"{c['title']}\n{c['content']}" for c in chunks]
        vectors = embed_texts(texts)
        self._save_index(vectors, chunks)

    def _save_index(self, vectors: np.ndarray, chunks: List[dict]) -> None:
        import faiss

        dim = vectors.shape[1]
        index = faiss.IndexFlatIP(dim)
        faiss.normalize_L2(vectors)
        index.add(vectors)
        faiss.write_index(index, str(INDEX_PATH))
        META_PATH.write_text(json.dumps(chunks, ensure_ascii=False, indent=2), encoding="utf-8")
        self.index = index
        self.chunks = chunks

    def _load(self) -> None:
        import faiss

        self.index = faiss.read_index(str(INDEX_PATH))
        self.chunks = json.loads(META_PATH.read_text(encoding="utf-8"))

    def search(self, query: str, top_k: int = 3) -> List[Tuple[dict, float]]:
        self.build_if_needed()
        if not self.chunks or self.index is None:
            return []
        q = embed_texts([query])
        import faiss

        faiss.normalize_L2(q)
        scores, indices = self.index.search(q, min(top_k, len(self.chunks)))
        results = []
        for score, idx in zip(scores[0], indices[0]):
            if idx < 0:
                continue
            results.append((self.chunks[idx], float(score)))
        return results
