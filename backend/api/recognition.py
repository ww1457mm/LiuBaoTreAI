from fastapi import APIRouter, Depends, Form, File, UploadFile, HTTPException
from sqlalchemy.orm import Session

from backend.database.mysql import get_db
from backend.models.record import RecognitionRecord
from backend.models.user import User
from backend.services.recognition_service import save_and_recognize
from backend.utils.validators import sanitize_openid, sanitize_task_type

router = APIRouter(prefix="/api", tags=["recognition"])


ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
MAX_IMAGE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/recognition")
async def recognize(
    openid: str = Form(...),
    task: str = Form("disease"),
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    print(f"[recognition] openid received: {openid}")
    openid = sanitize_openid(openid) or openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}

    # 验证文件类型
    content_type = file.content_type or "application/octet-stream"
    if content_type not in ALLOWED_IMAGE_TYPES:
        return {"code": 400, "message": "仅支持 JPG/PNG/WEBP 格式图片"}

    content = await file.read()
    if len(content) > MAX_IMAGE_SIZE:
        return {"code": 400, "message": "图片大小不能超过 10MB"}

    safe_task = sanitize_task_type(task)
    result = save_and_recognize(content, file.filename or "image.jpg", task=safe_task)
    record = RecognitionRecord(
        user_id=user.id,
        image_url=result["image_url"],
        result=result["category"],
        confidence=str(result["confidence"]),
        description=result.get("description", ""),
        suggestion=result.get("suggestion", ""),
        task_type=safe_task,
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
            "task": safe_task,
        },
    }
