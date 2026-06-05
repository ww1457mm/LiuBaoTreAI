from typing import List, Optional

from sqlalchemy.orm import Session

from ai_models.rag.retriever import retrieve
from backend.models.knowledge import KnowledgeBase


def list_knowledge(db: Session, category: Optional[str] = None) -> List[dict]:
    q = db.query(KnowledgeBase)
    if category:
        q = q.filter(KnowledgeBase.category == category)
    items = q.order_by(KnowledgeBase.id).all()
    return [
        {
            "id": k.id,
            "title": k.title,
            "content": k.content[:200] + ("..." if len(k.content) > 200 else ""),
            "source": k.source,
            "category": k.category,
        }
        for k in items
    ]


def get_knowledge_detail(db: Session, kid: int) -> Optional[dict]:
    k = db.query(KnowledgeBase).filter(KnowledgeBase.id == kid).first()
    if not k:
        return None
    return {
        "id": k.id,
        "title": k.title,
        "content": k.content,
        "source": k.source,
        "category": k.category,
    }


def search_knowledge(query: str) -> List[dict]:
    return retrieve(query, top_k=5)
