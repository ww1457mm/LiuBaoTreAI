import json
from typing import List, Optional

from ai_models.rag.generator import rag_answer


def ask_question(question: str, history: Optional[List[dict]] = None) -> dict:
    data = rag_answer(question, history=history)
    return {
        "answer": data["answer"],
        "references": data["references"],
        "recommendations": data["recommendations"],
        "references_json": json.dumps(data["references"], ensure_ascii=False),
    }
