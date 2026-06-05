from __future__ import annotations

from typing import List, Optional

from ai_models.llm.dashscope_client import chat_completion
from ai_models.rag.retriever import retrieve


def rag_answer(question: str, history: Optional[List[dict]] = None) -> dict:
    docs = retrieve(question, top_k=3)
    context = "\n\n".join(
        f"[{d['title']}]（来源：{d['source']}）\n{d['content']}" for d in docs
    )
    answer = chat_completion(question, context=context or None, history=history)
    return {
        "answer": answer,
        "references": docs,
        "recommendations": [d["title"] for d in docs[:3]],
    }
