"""
聊天服务模块 - 封装 RAG 问答的业务逻辑

核心功能：
1. 调用 RAG 生成器获取回答
2. 格式化返回数据
3. 生成 JSON 格式的参考资料（用于数据库存储）

职责：
- 作为 API 层和 AI 模型层的桥梁
- 处理数据格式转换
- 提供统一的问答接口

调用链路：
    API (chat.py)
        ↓
    服务层 (chat_service.py)  ← 你在这里
        ↓
    RAG 生成器 (generator.py)
        ↓
    检索器 (retriever.py) + LLM (dashscope_client.py)
"""

import json
from typing import List, Optional

from ai_models.rag.generator import rag_answer


def ask_question(question: str, history: Optional[List[dict]] = None) -> dict:
    """
    执行问答请求

    参数:
        question: 用户问题
        history: 可选的对话历史

    返回:
        字典:
        {
            "answer": str,              # AI 回答
            "references": list,         # 参考资料列表（字典格式）
            "recommendations": list,    # 推荐主题列表
            "references_json": str      # 参考资料 JSON 字符串（用于数据库存储）
        }

    工作流程:
    1. 调用 rag_answer() 获取 RAG 生成结果
    2. 提取 answer、references、recommendations
    3. 将 references 序列化为 JSON 字符串
    4. 返回格式化的结果

    数据转换:
    - references: 原始字典列表，用于 API 响应
    - references_json: JSON 字符串，用于数据库存储
    """
    # 调用 RAG 生成器
    data = rag_answer(question, history=history)

    # 格式化返回结果
    return {
        "answer": data["answer"],
        "references": data["references"],
        "recommendations": data["recommendations"],
        # 将参考资料序列化为 JSON 字符串，用于数据库存储
        "references_json": json.dumps(data["references"], ensure_ascii=False),
    }
