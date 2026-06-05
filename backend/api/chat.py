import json
from typing import List, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.mysql import get_db
from backend.models.record import QARecord
from backend.models.user import User
from backend.services.chat_service import ask_question

router = APIRouter(prefix="/api", tags=["chat"])


class ChatMessage(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    openid: str
    question: str
    history: Optional[List[ChatMessage]] = None


@router.post("/chat")
def chat(body: ChatRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.openid == body.openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}
    history = [m.model_dump() for m in body.history] if body.history else None
    result = ask_question(body.question, history=history)
    record = QARecord(
        user_id=user.id,
        question=body.question,
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
