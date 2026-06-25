from __future__ import annotations

import time
from typing import List, Optional

import httpx

from ai_models.llm.qwen_config import (
    OLLAMA_BASE_URL,
    OLLAMA_MODEL,
    OLLAMA_TIMEOUT,
    SYSTEM_PROMPT,
)

MAX_RETRIES = 3
INITIAL_DELAY = 1.0


def chat_completion(
    question: str,
    context: Optional[str] = None,
    history: Optional[List[dict]] = None,
) -> str:
    """调用本地 Ollama Qwen 模型；不可用时返回本地兜底回答。"""
    messages = _build_messages(question, context=context, history=history)

    last_error: Optional[Exception] = None
    for attempt in range(MAX_RETRIES):
        for model in _candidate_models(OLLAMA_MODEL):
            try:
                content = _ollama_chat(model, messages)
                if content:
                    return content
                last_error = ValueError("Empty response from Ollama")
            except Exception as exc:
                last_error = exc
                continue

        if attempt < MAX_RETRIES - 1:
            delay = INITIAL_DELAY * (2 ** attempt)
            time.sleep(delay)

    return _fallback_answer(question, context, error=last_error)


def _build_messages(
    question: str,
    context: Optional[str] = None,
    history: Optional[List[dict]] = None,
) -> List[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    if history:
        for item in history[-6:]:
            role = item.get("role")
            content = item.get("content")
            if role in {"user", "assistant"} and content:
                messages.append({"role": role, "content": content})

    user_content = question
    if context:
        user_content = f"参考资料：\n{context}\n\n用户问题：{question}"
    messages.append({"role": "user", "content": user_content})
    return messages


def _candidate_models(model: str) -> List[str]:
    candidates = [model]
    if model == "qwen2.5:1.5b":
        candidates.append("qwen2.5-1.5b")
    elif model == "qwen2.5-1.5b":
        candidates.append("qwen2.5:1.5b")
    return list(dict.fromkeys(candidates))


def _ollama_chat(model: str, messages: List[dict]) -> str:
    resp = httpx.post(
        f"{OLLAMA_BASE_URL}/api/chat",
        json={
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": 0.7,
                "num_predict": 1500,
            },
        },
        timeout=OLLAMA_TIMEOUT,
    )
    resp.raise_for_status()
    data = resp.json()
    message = data.get("message") or {}
    return (message.get("content") or "").strip()


def _fallback_answer(
    question: str,
    context: Optional[str] = None,
    error: Optional[Exception] = None,
) -> str:
    prefix = "【本地兜底】Ollama 模型暂时不可用"
    if error:
        prefix += f"（{error}）"
    prefix += "。"

    if context:
        return (
            f"{prefix}\n\n根据知识库检索，为您整理如下：\n\n{context[:800]}\n\n"
            f"针对「{question}」，建议结合上述资料进一步了解六堡茶相关知识。"
        )
    return (
        f"{prefix}\n\n关于「{question}」：六堡茶是广西梧州特产黑茶，以红、浓、陈、醇著称。"
        "请确认 Ollama 已启动，并已拉取 qwen2.5:1.5b 或配置 OLLAMA_MODEL。"
    )
