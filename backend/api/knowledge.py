from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from backend.database.mysql import get_db
from backend.services import knowledge_service

router = APIRouter(prefix="/api", tags=["knowledge"])


@router.get("/knowledge")
def get_knowledge_list(
    category: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    items = knowledge_service.list_knowledge(db, category=category)
    return {"code": 0, "data": items}


@router.get("/knowledge/search/query")
def search_knowledge(q: str = Query(..., min_length=1)):
    items = knowledge_service.search_knowledge(q)
    return {"code": 0, "data": items}


@router.get("/knowledge/{kid}")
def get_knowledge_detail(kid: int, db: Session = Depends(get_db)):
    item = knowledge_service.get_knowledge_detail(db, kid)
    if not item:
        raise HTTPException(404, "文章不存在")
    return {"code": 0, "data": item}
