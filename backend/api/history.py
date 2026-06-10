import json
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.mysql import get_db
from backend.models.record import Favorite, QARecord, RecognitionRecord
from backend.models.user import User
from backend.utils.validators import (
    sanitize_fav_type,
    sanitize_openid,
    sanitize_page_params,
    sanitize_html,
)

router = APIRouter(prefix="/api", tags=["history"])


class FavoriteRequest(BaseModel):
    openid: str
    fav_type: str
    target_id: int = 0
    title: str = ""
    content: str = ""


@router.get("/history")
def get_history(
    openid: str = Query(...),
    type: str = Query("all"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    openid = sanitize_openid(openid) or openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}

    page, page_size = sanitize_page_params(page, page_size, max_page_size=100)
    limit = page_size
    offset = (page - 1) * page_size
    data = {}

    if type in ("all", "recognition"):
        query = (
            db.query(RecognitionRecord)
            .filter(RecognitionRecord.user_id == user.id)
            .order_by(RecognitionRecord.create_time.desc())
        )
        total = query.count()
        records = query.offset(offset).limit(limit).all()
        data["recognition"] = {
            "items": [
                {
                    "id": r.id,
                    "image_url": r.image_url,
                    "result": r.result,
                    "confidence": r.confidence,
                    "description": r.description,
                    "suggestion": r.suggestion,
                    "task_type": r.task_type,
                    "create_time": r.create_time.isoformat() if r.create_time else "",
                }
                for r in records
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": (page * page_size) < total,
        }
    if type in ("all", "qa"):
        query = (
            db.query(QARecord)
            .filter(QARecord.user_id == user.id)
            .order_by(QARecord.create_time.desc())
        )
        total = query.count()
        records = query.offset(offset).limit(limit).all()
        data["qa"] = {
            "items": [
                {
                    "id": r.id,
                    "question": r.question,
                    "answer": r.answer,
                    "references": json.loads(r.references_json or "[]"),
                    "create_time": r.create_time.isoformat() if r.create_time else "",
                }
                for r in records
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "has_more": (page * page_size) < total,
        }
    return {"code": 0, "data": data}


@router.delete("/history/recognition/{rid}")
def delete_recognition_record(
    rid: int,
    openid: str = Query(...),
    db: Session = Depends(get_db),
):
    """删除单条识别记录"""
    openid = sanitize_openid(openid) or openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}
    record = db.query(RecognitionRecord).filter(
        RecognitionRecord.id == rid, RecognitionRecord.user_id == user.id
    ).first()
    if record:
        db.delete(record)
        db.commit()
    return {"code": 0, "message": "已删除"}


@router.delete("/history/qa/{qid}")
def delete_qa_record(
    qid: int,
    openid: str = Query(...),
    db: Session = Depends(get_db),
):
    """删除单条问答记录"""
    openid = sanitize_openid(openid) or openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}
    record = db.query(QARecord).filter(
        QARecord.id == qid, QARecord.user_id == user.id
    ).first()
    if record:
        db.delete(record)
        db.commit()
    return {"code": 0, "message": "已删除"}


@router.post("/favorite")
def add_favorite(body: FavoriteRequest, db: Session = Depends(get_db)):
    openid = sanitize_openid(body.openid) or body.openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}
    fav = Favorite(
        user_id=user.id,
        fav_type=sanitize_fav_type(body.fav_type),
        target_id=body.target_id or 0,
        title=sanitize_html(body.title, max_len=256),
        content=sanitize_html(body.content, max_len=10000),
    )
    db.add(fav)
    db.commit()
    db.refresh(fav)
    return {"code": 0, "message": "收藏成功", "data": fav.id}


@router.get("/favorite")
def list_favorites(
    openid: str = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    openid = sanitize_openid(openid) or openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}
    page, page_size = sanitize_page_params(page, page_size)
    offset = (page - 1) * page_size
    query = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id)
        .order_by(Favorite.create_time.desc())
    )
    total = query.count()
    items = query.offset(offset).limit(page_size).all()
    return {
        "code": 0,
        "data": [
            {
                "id": f.id,
                "fav_type": f.fav_type,
                "target_id": f.target_id,
                "title": f.title,
                "content": f.content,
                "create_time": f.create_time.isoformat() if f.create_time else "",
            }
            for f in items
        ],
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": (page * page_size) < total,
    }


@router.delete("/favorite/{fid}")
def delete_favorite(
    fid: int,
    openid: str = Query(...),
    db: Session = Depends(get_db),
):
    openid = sanitize_openid(openid) or openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}
    fav = db.query(Favorite).filter(Favorite.id == fid, Favorite.user_id == user.id).first()
    if fav:
        db.delete(fav)
        db.commit()
    return {"code": 0, "message": "已取消收藏"}
