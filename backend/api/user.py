import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session

from backend.database.mysql import get_db
from backend.models.user import User

router = APIRouter(prefix="/api/user", tags=["user"])


class LoginRequest(BaseModel):
    code: str = ""
    openid: str = ""


class ProfileUpdate(BaseModel):
    openid: str
    nickname: str = ""
    avatar: str = ""


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """微信小程序登录；开发模式可用 openid 直接标识用户。"""
    openid = body.openid
    if not openid:
        openid = f"dev_{body.code or 'guest'}"
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        user = User(openid=openid, nickname="茶友", avatar="")
        db.add(user)
        db.commit()
        db.refresh(user)
    return {
        "id": user.id,
        "openid": user.openid,
        "nickname": user.nickname,
        "avatar": user.avatar,
    }


@router.get("/profile")
def get_profile(openid: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    return {
        "id": user.id,
        "openid": user.openid,
        "nickname": user.nickname,
        "avatar": user.avatar,
    }


@router.put("/profile")
def update_profile(body: ProfileUpdate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.openid == body.openid).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    if body.nickname:
        user.nickname = body.nickname
    if body.avatar:
        user.avatar = body.avatar
    db.commit()
    return {"message": "更新成功"}
