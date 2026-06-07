import os
import httpx
from typing import Optional

WECHAT_APP_ID = os.getenv("WECHAT_APP_ID", "")
WECHAT_APP_SECRET = os.getenv("WECHAT_APP_SECRET", "")
WECHAT_API_BASE = "https://api.weixin.qq.com"


class WeChatError(Exception):
    """微信 API 错误"""
    def __init__(self, errcode: int, errmsg: str):
        self.errcode = errcode
        self.errmsg = errmsg
        super().__init__(f"[{errcode}] {errmsg}")


def code2session(code: str) -> dict:
    """
    通过微信登录 code 换取 openid 和 session_key。
    文档: https://developers.weixin.qq.com/miniprogram/dev/OpenApiDoc/user-login/code2Session.html
    """
    if not WECHAT_APP_ID or not WECHAT_APP_SECRET:
        raise WeChatError(-1, "未配置 WECHAT_APP_ID 或 WECHAT_APP_SECRET")

    url = f"{WECHAT_API_BASE}/sns/jscode2session"
    params = {
        "appid": WECHAT_APP_ID,
        "secret": WECHAT_APP_SECRET,
        "js_code": code,
        "grant_type": "authorization_code",
    }
    try:
        resp = httpx.get(url, params=params, timeout=10.0)
        resp.raise_for_status()
        data = resp.json()
    except httpx.HTTPError as exc:
        raise WeChatError(-2, f"请求微信接口失败: {exc}")

    if "errcode" in data and data["errcode"] != 0:
        raise WeChatError(data["errcode"], data.get("errmsg", "未知错误"))

    return {
        "openid": data.get("openid", ""),
        "session_key": data.get("session_key", ""),
        "unionid": data.get("unionid", ""),
    }
