from typing import List, Optional, Tuple
import time
from sqlalchemy.orm import Session
from ai_models.rag.retriever import retrieve
from backend.models.knowledge import KnowledgeBase

# Simple in-memory cache: (query_key) -> (result, timestamp)
_cache: dict[str, Tuple[List[dict], float]] = {}
_CACHE_TTL = 300  # 5 minutes


def _cache_get(key: str) -> Optional[List[dict]]:
    item = _cache.get(key)
    if item and (time.time() - item[1]) < _CACHE_TTL:
        return item[0]
    return None


def _cache_set(key: str, data: List[dict]) -> None:
    _cache[key] = (data, time.time())


def _attach_db_ids(items: List[dict], db: Session) -> List[dict]:
    """根据标题匹配，为搜索结果附加数据库 ID。"""
    if not items:
        return items
    titles = [it["title"] for it in items]
    records = (
        db.query(KnowledgeBase.id, KnowledgeBase.title)
        .filter(KnowledgeBase.title.in_(titles))
        .all()
    )
    id_map = {title: kid for kid, title in records}
    for item in items:
        item["id"] = id_map.get(item["title"], 0)
    return items


def list_knowledge(
    db: Session,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[dict], int]:
    cache_key = f"list:{category}:{page}:{page_size}"
    cached = _cache_get(cache_key)
    if cached:
        total = db.query(KnowledgeBase).filter(
            KnowledgeBase.category == category if category else True
        ).count()
        return cached, total

    q = db.query(KnowledgeBase)
    if category:
        q = q.filter(KnowledgeBase.category == category)
    total = q.count()
    items = (
        q.order_by(KnowledgeBase.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    result = [
        {
            "id": k.id,
            "title": k.title,
            "content": k.content[:200] + ("..." if len(k.content) > 200 else ""),
            "source": k.source,
            "category": k.category,
        }
        for k in items
    ]
    _cache_set(cache_key, result)
    return result, total


def get_knowledge_detail(db: Session, kid: int) -> Optional[dict]:
    cache_key = f"detail:{kid}"
    cached = _cache_get(cache_key)
    if cached:
        return cached[0] if cached else None
    k = db.query(KnowledgeBase).filter(KnowledgeBase.id == kid).first()
    if not k:
        return None
    result = {
        "id": k.id,
        "title": k.title,
        "content": k.content,
        "source": k.source,
        "category": k.category,
    }
    _cache_set(cache_key, [result])
    return result


def search_knowledge(
    query: str,
    page: int = 1,
    page_size: int = 10,
    db: Optional[Session] = None,
) -> List[dict]:
    cache_key = f"search:{query}:{page}:{page_size}"
    cached = _cache_get(cache_key)
    if cached:
        return cached
    results = retrieve(query, top_k=min(page_size * 2, 20))
    offset = (page - 1) * page_size
    paginated = results[offset:offset + page_size]
    # 向量搜索结果不带 DB id，需要通过标题匹配
    if db:
        paginated = _attach_db_ids(paginated, db)
    _cache_set(cache_key, paginated)
    return paginated
