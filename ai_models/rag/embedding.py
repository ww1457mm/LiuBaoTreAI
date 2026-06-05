from __future__ import annotations

import os
from typing import List

import numpy as np

SILICONFLOW_API_KEY = os.getenv("SILICONFLOW_API_KEY", "")
SILICONFLOW_EMBED_URL = os.getenv(
    "SILICONFLOW_EMBED_URL",
    "https://api.siliconflow.cn/v1/embeddings",
)
EMBED_MODEL = os.getenv("EMBED_MODEL", "BAAI/bge-large-zh-v1.5")
_EMBED_CACHE: dict[str, np.ndarray] = {}


def embed_texts(texts: List[str]) -> np.ndarray:
    if not texts:
        return np.zeros((0, 768), dtype=np.float32)

    uncached = [t for t in texts if t not in _EMBED_CACHE]
    if uncached:
        vectors = _request_embeddings(uncached)
        for text, vec in zip(uncached, vectors):
            _EMBED_CACHE[text] = vec

    return np.stack([_EMBED_CACHE[t] for t in texts]).astype(np.float32)


def _request_embeddings(texts: List[str]) -> List[np.ndarray]:
    if SILICONFLOW_API_KEY:
        try:
            import httpx

            resp = httpx.post(
                SILICONFLOW_EMBED_URL,
                headers={"Authorization": f"Bearer {SILICONFLOW_API_KEY}"},
                json={"model": EMBED_MODEL, "input": texts},
                timeout=60.0,
            )
            resp.raise_for_status()
            data = resp.json()["data"]
            data.sort(key=lambda x: x["index"])
            return [np.array(item["embedding"], dtype=np.float32) for item in data]
        except Exception:
            pass
    return [_local_hash_embedding(t) for t in texts]


def _local_hash_embedding(text: str, dim: int = 768) -> np.ndarray:
    """无 API 时的确定性伪向量，保证 FAISS 可运行。"""
    rng = np.random.default_rng(abs(hash(text)) % (2**32))
    vec = rng.standard_normal(dim).astype(np.float32)
    norm = np.linalg.norm(vec)
    if norm > 0:
        vec /= norm
    return vec
