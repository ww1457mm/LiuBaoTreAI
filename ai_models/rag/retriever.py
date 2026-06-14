"""
检索器模块 - 封装向量搜索，提供简洁的检索接口

核心功能：
1. 单例模式管理 VectorStore 实例
2. 提供简洁的检索接口
3. 格式化搜索结果

职责：
- 作为 RAG 系统的检索组件
- 将用户问题转换为相关知识块
- 返回带有相似度分数的结构化结果

使用方法:
    from ai_models.rag.retriever import retrieve

    # 检索与问题相关的知识块
    results = retrieve("六堡茶的冲泡方法", top_k=3)

    # results 结构:
    # [
    #     {
    #         "title": "冲泡方法",
    #         "content": "...",
    #         "source": "knowledge_base/brew/冲泡方法.txt",
    #         "category": "brew",
    #         "score": 0.8523
    #     },
    #     ...
    # ]
"""

from __future__ import annotations

from typing import List

from ai_models.rag.vector_store import VectorStore

# 全局单例：VectorStore 实例
# 延迟初始化，首次调用 get_store() 时创建
_store: VectorStore | None = None


def get_store() -> VectorStore:
    """
    获取 VectorStore 单例

    返回:
        VectorStore: 已初始化的向量存储实例

    设计模式:
    - 单例模式：全局只有一个 VectorStore 实例
    - 延迟初始化：首次调用时才创建和构建索引
    - 线程安全：Python 的 GIL 保证了原子性

    优点:
    - 避免重复构建索引（耗时操作）
    - 节省内存（索引文件只加载一次）
    """
    global _store
    if _store is None:
        _store = VectorStore()
        # 首次创建时构建索引
        _store.build_if_needed()
    return _store


def retrieve(query: str, top_k: int = 3) -> List[dict]:
    """
    检索与查询文本相关的知识块

    参数:
        query: 查询文本（用户问题）
        top_k: 返回结果数量，默认 3

    返回:
        列表，每个元素是一个字典:
        {
            "title": str,      # 知识块标题
            "content": str,    # 知识块内容
            "source": str,     # 来源文件路径
            "category": str,   # 分类（如 history/process/brew）
            "score": float     # 相似度分数，保留 4 位小数
        }

    工作流程:
    1. 获取 VectorStore 单例
    2. 调用 search 方法执行向量搜索
    3. 将结果格式化为标准字典格式
    4. 返回结构化的检索结果

    使用场景:
    - RAG 问答：检索相关知识作为 LLM 的参考
    - 知识库搜索：语义搜索相关文章
    """
    # 获取向量存储实例并执行搜索
    results = get_store().search(query, top_k=top_k)

    # 格式化搜索结果
    return [
        {
            "title": chunk["title"],
            "content": chunk["content"],
            "source": chunk["source"],
            "category": chunk.get("category", ""),
            "score": round(score, 4),  # 保留 4 位小数
        }
        for chunk, score in results
    ]
