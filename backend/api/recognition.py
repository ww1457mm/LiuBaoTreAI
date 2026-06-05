from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.orm import Session

from backend.database.mysql import get_db
from backend.models.record import RecognitionRecord
from backend.models.user import User
from backend.services.recognition_service import save_and_recognize

router = APIRouter(prefix="/api", tags=["recognition"])


@router.post("/recognition")
async def recognize(
    openid: str = Form(...),
    task: str = Form("variety"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}
    content = await file.read()
    result = save_and_recognize(content, file.filename or "image.jpg", task=task)
    record = RecognitionRecord(
        user_id=user.id,
        image_url=result["image_url"],
        result=result["category"],
        confidence=str(result["confidence"]),
        description=result.get("description", ""),
        suggestion=result.get("suggestion", ""),
        task_type=task,
    )
    db.add(record)
    db.commit()
    db.refresh(record)
    return {
        "code": 0,
        "data": {
            "id": record.id,
            "category": result["category"],
            "confidence": result["confidence"],
            "description": result.get("description", ""),
            "suggestion": result.get("suggestion", ""),
            "image_url": result["image_url"],
            "task": task,
        },
    }
