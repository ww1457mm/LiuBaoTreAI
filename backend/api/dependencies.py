from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.mysql import get_db
from backend.models.user import User


def get_current_user(openid: str, db: Session = Depends(get_db)) -> User:
    """根据 openid 获取当前用户，不存在则抛 401。"""
    if not openid or len(openid) < 4:
        raise HTTPException(status_code=401, detail="无效的用户身份")
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(status_code=401, detail="用户不存在，请先登录")
    return user
