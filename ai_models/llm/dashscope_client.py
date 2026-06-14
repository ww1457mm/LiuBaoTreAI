"""
LLM 客户端模块 - 阿里云百炼 API 调用封装

核心功能：
1. 调用阿里云百炼（DashScope）的 OpenAI 兼容接口
2. 支持多轮对话（传入历史记录）
3. 自动重试机制（指数退避）
4. 无 API 密钥时提供本地兜底回答

技术细节：
- 使用 OpenAI SDK 调用阿里云百炼 API
- 支持通义千问系列模型（qwen-plus/qwen-turbo 等）
- 消息格式遵循 OpenAI Chat Completion API 规范
- 温度参数控制回答的随机性（0.7 = 适度创造）

API 兼容性：
阿里云百炼提供 OpenAI 兼容接口，可以使用 OpenAI SDK 直接调用：
    client = OpenAI(api_key="...", base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
"""

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

# ========== 重试配置 ==========
# 最大重试次数
MAX_RETRIES = 3

# 初始延迟（秒），后续按指数增长：1s -> 2s -> 4s
INITIAL_DELAY = 1.0


def chat_completion(
    question: str,
    context: Optional[str] = None,
    history: Optional[List[dict]] = None,
) -> str:
    """
    调用 LLM 生成回答

    参数:
        question: 用户问题
        context: 参考资料（RAG 检索到的知识块）
        history: 对话历史，格式 [{"role": "user"/"assistant", "content": "..."}]

    返回:
        str: LLM 生成的回答文本

    消息构造流程:

    1. System Prompt（系统提示）
       - 定义 AI 的角色和行为规范
       - 告知 AI 是六堡茶领域专业助手

    2. History（对话历史）
       - 最多保留最近 6 条消息（3 轮对话）
       - 保持上下文连贯性

    3. User Message（用户消息）
       - 如果有参考资料，构造为: 参考资料 + 用户问题
       - 如果无参考资料，直接使用用户问题

    降级策略:
    - 无 API 密钥时，返回本地兜底回答
    - API 调用失败时，重试后降级为本地回答
    """
    # ========== 构造消息列表 ==========
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    # 添加对话历史（最近 6 条，即 3 轮对话）
    if history:
        for item in history[-6:]:
            messages.append({"role": item["role"], "content": item["content"]})

    # 构造用户消息
    user_content = question
    if context:
        # 有参考资料时，将资料和问题组合
        user_content = f"参考资料：\n{context}\n\n用户问题：{question}"

    messages.append({"role": "user", "content": user_content})

    # ========== 检查 API 密钥 ==========
    if not DASHSCOPE_API_KEY:
        # 无 API 密钥，返回本地兜底回答
        return _fallback_answer(question, context)

    # ========== 调用 LLM API ==========
    last_error: Optional[Exception] = None

    for attempt in range(MAX_RETRIES):
        try:
            from openai import OpenAI

            # 创建 OpenAI 客户端（使用阿里云百炼的 base_url）
            client = OpenAI(
                api_key=DASHSCOPE_API_KEY,
                base_url=DASHSCOPE_BASE_URL,
                timeout=30.0,  # 30 秒超时
            )

            # 调用 Chat Completion API
            resp = client.chat.completions.create(
                model=QWEN_MODEL,  # 使用的模型（如 qwen-plus）
                messages=messages,
                temperature=0.7,  # 温度：0.7 = 适度随机
                max_tokens=3000,  # 最大生成 3000 tokens，支持详细回答
            )

            # 提取回答内容
            content = resp.choices[0].message.content
            if content:
                return content

            # 空回答，记录错误
            last_error = ValueError("Empty response from LLM")

        except Exception as exc:
            last_error = exc
            if attempt < MAX_RETRIES - 1:
                # 指数退避：1s -> 2s -> 4s
                delay = INITIAL_DELAY * (2 ** attempt)
                time.sleep(delay)
                continue

    # 所有重试失败，返回本地兜底回答
    return _fallback_answer(question, context)


def _fallback_answer(question: str, context: Optional[str] = None) -> str:
    """
    本地兜底回答生成

    参数:
        question: 用户问题
        context: 参考资料（可选）

    返回:
        str: 本地生成的回答

    使用场景:
    - 未配置 API 密钥
    - API 调用失败（网络问题、限流等）

    特点:
    - 无需外部 API 依赖
    - 如果有参考资料，直接展示
    - 如果无资料，提供通用介绍
    """
    if context:
        # 有参考资料时，直接展示资料（截取前 800 字符）
        return (
            f"【本地模式】根据知识库检索，为您整理如下：\n\n{context[:800]}\n\n"
            f"针对「{question}」，建议结合上述资料进一步了解六堡茶相关知识。"
        )

    # 无参考资料时，提供通用介绍
    return (
        f"【本地模式】关于「{question}」：六堡茶是广西梧州特产黑茶，以红、浓、陈、醇著称。"
        "您可询问历史文化、制作工艺、冲泡方法、存储收藏或健康功效等，"
        "配置 DASHSCOPE_API_KEY 后可启用云端大模型获得更智能的回答。"
    )
