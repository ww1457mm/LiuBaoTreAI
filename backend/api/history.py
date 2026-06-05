import json
from typing import Optional

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.mysql import get_db
from backend.models.record import Favorite, QARecord, RecognitionRecord
from backend.models.user import User

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
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}
    data = {}
    if type in ("all", "recognition"):
        records = (
            db.query(RecognitionRecord)
            .filter(RecognitionRecord.user_id == user.id)
            .order_by(RecognitionRecord.create_time.desc())
            .limit(50)
            .all()
        )
        data["recognition"] = [
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
        ]
    if type in ("all", "qa"):
        records = (
            db.query(QARecord)
            .filter(QARecord.user_id == user.id)
            .order_by(QARecord.create_time.desc())
            .limit(50)
            .all()
        )
        data["qa"] = [
            {
                "id": r.id,
                "question": r.question,
                "answer": r.answer,
                "references": json.loads(r.references_json or "[]"),
                "create_time": r.create_time.isoformat() if r.create_time else "",
            }
            for r in records
        ]
    return {"code": 0, "data": data}


@router.post("/favorite")
def add_favorite(body: FavoriteRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.openid == body.openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}
    fav = Favorite(
        user_id=user.id,
        fav_type=body.fav_type,
        target_id=body.target_id,
        title=body.title,
        content=body.content,
    )
    db.add(fav)
    db.commit()
    return {"code": 0, "message": "收藏成功"}


@router.get("/favorite")
def list_favorites(openid: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}
    items = (
        db.query(Favorite)
        .filter(Favorite.user_id == user.id)
        .order_by(Favorite.create_time.desc())
        .all()
    )
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
    }


@router.delete("/favorite/{fid}")
def delete_favorite(fid: int, openid: str = Query(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}
    fav = db.query(Favorite).filter(Favorite.id == fid, Favorite.user_id == user.id).first()
    if fav:
        db.delete(fav)
        db.commit()
    return {"code": 0, "message": "已取消收藏"}
