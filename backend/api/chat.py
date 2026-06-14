"""
聊天问答 API 模块 - 处理用户的 AI 问答请求

API 端点：
- POST /api/chat: 接收用户问题，返回 AI 回答

请求流程：
1. 验证用户身份（openid）
2. 清洗和验证问题内容
3. 调用 RAG 服务生成回答
4. 保存问答记录到数据库
5. 返回回答和参考资料

安全措施：
- 用户身份验证（必须登录）
- 输入内容清洗（防 XSS、SQL 注入）
- 问题长度限制（500 字符）
"""

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

# 创建路由器，所有路由以 /api 开头
router = APIRouter(prefix="/api", tags=["chat"])


class ChatMessage(BaseModel):
    """
    聊天消息模型 - 用于多轮对话历史

    属性:
        role: 消息角色，"user" 或 "assistant"
        content: 消息内容
    """
    role: str
    content: str


class ChatRequest(BaseModel):
    """
    聊天请求模型 - 定义请求参数和验证规则

    属性:
        openid: 用户唯一标识（微信 openid）
        question: 用户问题（1-500 字符）
        history: 可选的对话历史

    验证规则:
    - openid: 必填
    - question: 必填，长度 1-500 字符
    - history: 可选，用于多轮对话
    """
    openid: str = Field(..., description="用户 openid")
    question: str = Field(..., min_length=1, max_length=500, description="问题内容")
    history: Optional[List[ChatMessage]] = None


@router.post("/chat")
def chat(body: ChatRequest, db: Session = Depends(get_db)):
    """
    聊天问答接口

    参数:
        body: ChatRequest 请求体
        db: 数据库会话（依赖注入）

    返回:
        JSON 响应:
        {
            "code": 0,              # 状态码，0 表示成功
            "data": {
                "id": int,          # 问答记录 ID
                "answer": str,      # AI 回答
                "references": list, # 参考资料列表
                "recommendations": list  # 推荐的相关主题
            }
        }

    处理流程:
    1. 清洗 openid（防注入）
    2. 查询用户是否存在
    3. 清洗问题内容
    4. 调用 RAG 服务生成回答
    5. 保存问答记录到 qa_record 表
    6. 返回结果
    """
    # ========== 1. 用户身份验证 ==========
    # 清洗 openid，防止恶意输入
    openid = sanitize_openid(body.openid) or body.openid

    # 查询用户是否存在
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {"code": 401, "message": "请先登录"}

    # ========== 2. 输入清洗 ==========
    # 清洗问题内容，移除危险字符
    question = sanitize_question(body.question)

    # 转换对话历史格式
    history = [m.model_dump() for m in body.history] if body.history else None

    # ========== 3. 调用 RAG 服务 ==========
    # 生成 AI 回答（包含检索和生成两个阶段）
    result = ask_question(question, history=history)

    # ========== 4. 保存问答记录 ==========
    # 创建问答记录对象
    record = QARecord(
        user_id=user.id,  # 关联用户 ID
        question=question,
        answer=result["answer"],
        references_json=result["references_json"],  # 参考资料 JSON 字符串
    )

    # 保存到数据库
    db.add(record)
    db.commit()
    db.refresh(record)  # 刷新获取自增 ID

    # ========== 5. 返回结果 ==========
    return {
        "code": 0,
        "data": {
            "id": record.id,
            "answer": result["answer"],
            "references": result["references"],
            "recommendations": result["recommendations"],
        },
    }
