from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.mysql import get_db
from backend.models.journal import TeaJournal
from backend.models.user import User
from backend.utils.validators import sanitize_openid, sanitize_string, sanitize_html

router = APIRouter(prefix="/api", tags=["journal"])


class JournalCreate(BaseModel):
    openid: str
    tea_name: str = Field(..., max_length=128)
    tea_type: str = Field(default="", max_length=32)
    origin: str = Field(default="", max_length=128)
    brew_temp: str = Field(default="", max_length=16)
    brew_time: str = Field(default="", max_length=16)
    tea_amount: str = Field(default="", max_length=32)
    aroma_score: int = Field(default=3, ge=1, le=5)
    taste_score: int = Field(default=3, ge=1, le=5)
    overall_score: int = Field(default=3, ge=1, le=5)
    flavor_notes: str = Field(default="", max_length=256)
    notes: str = Field(default="", max_length=5000)
    image_url: str = Field(default="", max_length=512)


@router.post("/journal")
def create_journal(body: JournalCreate, db: Session = Depends(get_db)):
    openid = sanitize_openid(body.openid) or body.openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}

    entry = TeaJournal(
        user_id=user.id,
        tea_name=sanitize_string(body.tea_name, 128),
        tea_type=body.tea_type,
        origin=sanitize_string(body.origin, 128),
        brew_temp=body.brew_temp,
        brew_time=body.brew_time,
        tea_amount=body.tea_amount,
        aroma_score=body.aroma_score,
        taste_score=body.taste_score,
        overall_score=body.overall_score,
        flavor_notes=sanitize_string(body.flavor_notes, 256),
        notes=sanitize_html(body.notes, 5000),
        image_url=sanitize_string(body.image_url, 512),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"code": 0, "data": entry.id, "message": "记录成功"}


@router.get("/journal")
def list_journals(
    openid: str = Query(...),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    openid = sanitize_openid(openid) or openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}

    offset = (page - 1) * page_size
    query = db.query(TeaJournal).filter(TeaJournal.user_id == user.id).order_by(TeaJournal.create_time.desc())
    total = query.count()
    items = query.offset(offset).limit(page_size).all()
    return {
        "code": 0,
        "data": [_to_dict(j) for j in items],
        "total": total,
        "page": page,
        "page_size": page_size,
    }


@router.get("/journal/{jid}")
def get_journal(jid: int, openid: str = Query(...), db: Session = Depends(get_db)):
    openid = sanitize_openid(openid) or openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}

    entry = db.query(TeaJournal).filter(TeaJournal.id == jid, TeaJournal.user_id == user.id).first()
    if not entry:
        return {"code": 404, "message": "日记不存在"}
    return {"code": 0, "data": _to_dict(entry)}


@router.delete("/journal/{jid}")
def delete_journal(jid: int, openid: str = Query(...), db: Session = Depends(get_db)):
    openid = sanitize_openid(openid) or openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}

    entry = db.query(TeaJournal).filter(TeaJournal.id == jid, TeaJournal.user_id == user.id).first()
    if entry:
        db.delete(entry)
        db.commit()
    return {"code": 0, "message": "已删除"}


def _to_dict(j: TeaJournal) -> dict:
    return {
        "id": j.id,
        "tea_name": j.tea_name,
        "tea_type": j.tea_type,
        "origin": j.origin,
        "brew_temp": j.brew_temp,
        "brew_time": j.brew_time,
        "tea_amount": j.tea_amount,
        "aroma_score": j.aroma_score,
        "taste_score": j.taste_score,
        "overall_score": j.overall_score,
        "flavor_notes": j.flavor_notes.split(",") if j.flavor_notes else [],
        "notes": j.notes or "",
        "image_url": j.image_url or "",
        "create_time": j.create_time.isoformat() if j.create_time else "",
    }
