import json
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.mysql import get_db
from backend.models.record import QARecord
from backend.models.user import User
from backend.services.chat_service import ask_question
from backend.utils.validators import sanitize_question, sanitize_openid

router = APIRouter(prefix="/api", tags=["chat"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    openid: str = Field(..., description="用户 openid")
    question: str = Field(..., min_length=1, max_length=500, description="问题内容")
    history: Optional[List[ChatMessage]] = None


@router.post("/chat")
def chat(body: ChatRequest, db: Session = Depends(get_db)):
    openid = sanitize_openid(body.openid) or body.openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}
    question = sanitize_question(body.question)
    history = [m.model_dump() for m in body.history] if body.history else None
    result = ask_question(question, history=history)
    record = QARecord(
        user_id=user.id,
        question=question,
        answer=result["answer"],
        references_json=result["references_json"],
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {
        "code": 0,
        "data": {
            "id": record.id,
            "answer": result["answer"],
            "references": result["references"],
            "recommendations": result["recommendations"],
        },
    }
