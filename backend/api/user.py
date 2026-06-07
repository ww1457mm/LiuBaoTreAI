import os
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.mysql import get_db
from backend.models.user import User
from backend.utils.validators import sanitize_nickname, sanitize_openid, sanitize_string
from backend.utils.wechat import WeChatError, code2session
from backend.utils.logging_config import logger

router = APIRouter(prefix="/api/user", tags=["user"])


class LoginRequest(BaseModel):
    code: str = ""
    openid: str = ""


class WeChatLoginRequest(BaseModel):
    code: str = Field(..., description="wx.login() 返回的 code")


class ProfileUpdate(BaseModel):
    openid: str = Field(..., description="用户 openid")
    nickname: str = Field(default="", max_length=64)
    avatar: str = Field(default="", max_length=512)


@router.post("/login")
def login(body: LoginRequest, db: Session = Depends(get_db)):
    """微信小程序登录；开发模式可用 openid 直接标识用户。"""
    raw_openid = sanitize_openid(body.openid) or body.openid
    if not raw_openid:
        raw_openid = f"dev_{sanitize_string(body.code or 'guest', 64)[:32]}"
    user = db.query(User).filter(User.openid == raw_openid).first()
    if not user:
        user = User(openid=raw_openid, nickname="茶友", avatar="")
        db.add(user)
        db.commit()
        db.refresh(user)
    return {
        "id": user.id,
        "openid": user.openid,
        "nickname": user.nickname,
        "avatar": user.avatar,
    }


@router.post("/login/wechat")
def wechat_login(body: WeChatLoginRequest, db: Session = Depends(get_db)):
    """
    微信登录 - 通过 code 换取真实 openid。
    前端调用 wx.login() 获取 code，传入此接口完成登录。
    """
    if not body.code:
        return {"code": 400, "message": "code 不能为空"}

    try:
        session_data = code2session(body.code)
    except WeChatError as e:
        logger.warning(f"微信登录失败: {e}")
        # 微信接口不可用时，降级为开发模式
        dev_openid = f"dev_{body.code[:24]}"
        user = db.query(User).filter(User.openid == dev_openid).first()
        if not user:
            user = User(openid=dev_openid, nickname="茶友", avatar="")
            db.add(user)
            db.commit()
            db.refresh(user)
        return {
            "id": user.id,
            "openid": user.openid,
            "nickname": user.nickname,
            "avatar": user.avatar,
        }

    openid = session_data["openid"]
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        user = User(openid=openid, nickname="茶友", avatar="")
        db.add(user)
        db.commit()
        db.refresh(user)
        logger.info(f"新用户注册: {openid}")
    else:
        logger.info(f"用户登录: {openid}")

    return {
        "id": user.id,
        "openid": user.openid,
        "nickname": user.nickname,
        "avatar": user.avatar,
    }


@router.get("/profile")
def get_profile(openid: str, db: Session = Depends(get_db)):
    openid = sanitize_openid(openid) or openid
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
    openid = sanitize_openid(body.openid) or body.openid
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        raise HTTPException(404, "用户不存在")
    if body.nickname:
        user.nickname = sanitize_nickname(body.nickname)
    if body.avatar:
        user.avatar = sanitize_string(body.avatar, max_len=512)
    db.commit()
    return {"message": "更新成功"}
