from __future__ import annotations

import os
import time
from typing import List, Optional

from ai_models.llm.qwen_config import (
    DASHSCOPE_API_KEY,
    DASHSCOPE_BASE_URL,
    QWEN_MODEL,
    SYSTEM_PROMPT,
)

MAX_RETRIES = 3
INITIAL_DELAY = 1.0


def chat_completion(
    question: str,
    context: Optional[str] = None,
    history: Optional[List[dict]] = None,
) -> str:
    """调用阿里云百炼（OpenAI 兼容）接口；无密钥时返回本地兜底回答。"""
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for item in history[-6:]:
            messages.append({"role": item["role"], "content": item["content"]})
    user_content = question
    if context:
        user_content = f"参考资料：\n{context}\n\n用户问题：{question}"
    messages.append({"role": "user", "content": user_content})

    if not DASHSCOPE_API_KEY:
        return _fallback_answer(question, context)

    last_error: Optional[Exception] = None
    for attempt in range(MAX_RETRIES):
        try:
            from openai import OpenAI

            client = OpenAI(
                api_key=DASHSCOPE_API_KEY,
                base_url=DASHSCOPE_BASE_URL,
                timeout=30.0,
            )
            resp = client.chat.completions.create(
                model=QWEN_MODEL,
                messages=messages,
                temperature=0.7,
                max_tokens=1500,
            )
            content = resp.choices[0].message.content
            if content:
                return content
            last_error = ValueError("Empty response from LLM")
        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                delay = INITIAL_DELAY * (2 ** attempt)
                time.sleep(delay)
                continue

    return _fallback_answer(question, context)


def _fallback_answer(question: str, context: Optional[str] = None) -> str:
    if context:
        return (
            f"【本地模式】根据知识库检索，为您整理如下：\n\n{context[:800]}\n\n"
            f"针对「{question}」，建议结合上述资料进一步了解六堡茶相关知识。"
        )
    return (
        f"【本地模式】关于「{question}」：六堡茶是广西梧州特产黑茶，以红、浓、陈、醇著称。"
        "您可询问历史文化、制作工艺、冲泡方法、存储收藏或健康功效等，"
        "配置 DASHSCOPE_API_KEY 后可启用云端大模型获得更智能的回答。"
    )
