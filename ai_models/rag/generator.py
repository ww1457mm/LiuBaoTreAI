"""
RAG 生成器模块 - 检索增强生成（Retrieval-Augmented Generation）

核心功能：
1. 结合检索和生成，提供基于知识库的智能问答
2. 检索相关知识作为上下文
3. 调用 LLM 生成专业回答

RAG 架构：
    用户问题
        ↓
    向量检索（retriever）
        ↓
    相关知识块（top_k=3）
        ↓
    构造 Prompt（问题 + 参考资料）
        ↓
    LLM 生成回答（dashscope_client）
        ↓
    返回结果（回答 + 参考来源 + 推荐）

优点：
- 回答基于真实知识，减少幻觉
- 可追溯来源，增强可信度
- 知识库可动态更新，无需重新训练模型
"""

from __future__ import annotations

from typing import List, Optional

from ai_models.llm.dashscope_client import chat_completion
from ai_models.rag.retriever import retrieve


def rag_answer(question: str, history: Optional[List[dict]] = None) -> dict:
    """
    RAG 问答主函数

    参数:
        question: 用户问题
        history: 对话历史，格式 [{"role": "user"/"assistant", "content": "..."}]

    返回:
        字典:
        {
            "answer": str,           # LLM 生成的回答
            "references": list,      # 参考的知识块列表
            "recommendations": list  # 推荐的相关主题（前 3 个标题）
        }

    工作流程:

    1. 检索阶段（Retrieval）
       - 调用 retriever 检索与问题相关的知识块
       - 默认返回最相似的 3 个知识块
       - 每个知识块包含标题、内容、来源、分类、相似度

    2. 上下文构造
       - 将检索到的知识块格式化为文本
       - 格式: [标题]（来源：路径）\n内容
       - 多个知识块用空行分隔

    3. 生成阶段（Generation）
       - 将问题和上下文发送给 LLM
       - LLM 基于参考资料生成专业回答
       - 支持多轮对话（传入 history）

    4. 结果组装
       - answer: LLM 生成的回答
       - references: 原始知识块列表（用于前端展示来源）
       - recommendations: 推荐的相关主题标题

    示例:

        result = rag_answer("六堡茶怎么冲泡？")

        # result["answer"] = "冲泡六堡茶建议使用100℃沸水..."
        # result["references"] = [{"title": "冲泡方法", ...}]
        # result["recommendations"] = ["冲泡方法", "存储方法", "品鉴文化"]
    """

    # ========== 1. 检索阶段 ==========
    # 检索与问题相关的知识块
    docs = retrieve(question, top_k=3)

    # ========== 2. 上下文构造 ==========
    # 将知识块格式化为 LLM 可理解的上下文文本
    # 如果没有检索到相关文档，context 为 None，LLM 将基于自身知识回答
    context = None
    if docs:
        context = "\n\n".join(
            f"[{d['title']}]（来源：{d['source']}）\n{d['content']}"
            for d in docs
        )

    # ========== 3. 生成阶段 ==========
    # 调用 LLM 生成回答
    # context 为 None 时，LLM 会基于自身知识回答
    answer = chat_completion(question, context=context, history=history)

    # ========== 4. 结果组装 ==========
    return {
        "answer": answer,
        "references": docs,
        # 推荐前 3 个相关主题的标题
        "recommendations": [d["title"] for d in docs[:3]],
    }
