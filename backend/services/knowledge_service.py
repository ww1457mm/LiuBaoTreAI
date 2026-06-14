"""
知识库服务模块 - 提供知识文章的查询、搜索和缓存功能

核心功能：
1. 知识文章列表查询（支持分类筛选和分页）
2. 语义搜索（基于向量检索）
3. 文章详情查询
4. 内存缓存（5 分钟 TTL）

技术特点：
- 混合搜索策略：优先向量搜索，降级为数据库模糊搜索
- 内存缓存：减少数据库查询压力
- 标题匹配：为向量搜索结果附加数据库 ID

缓存策略：
- 缓存键格式: "list:{category}:{page}:{page_size}" / "detail:{kid}" / "search:{query}:{page}:{page_size}"
- 缓存时间: 5 分钟（300 秒）
- 缓存粒度: 按查询参数缓存
"""

from typing import List, Optional, Tuple
import time
from sqlalchemy.orm import Session
from sqlalchemy import or_
from ai_models.rag.retriever import retrieve
from backend.models.knowledge import KnowledgeBase

# ========== 缓存配置 ==========
# 内存缓存：键 -> (结果, 时间戳)
_cache: dict[str, Tuple[List[dict], float]] = {}

# 缓存过期时间：5 分钟
_CACHE_TTL = 300


def _cache_get(key: str) -> Optional[List[dict]]:
    """
    从缓存获取数据

    参数:
        key: 缓存键

    返回:
        缓存的数据，如果过期或不存在返回 None

    工作流程:
    1. 从缓存字典获取数据
    2. 检查是否过期（当前时间 - 缓存时间 > TTL）
    3. 未过期返回数据，过期返回 None
    """
    item = _cache.get(key)
    if item and (time.time() - item[1]) < _CACHE_TTL:
        return item[0]
    return None


def _cache_set(key: str, data: List[dict]) -> None:
    """
    将数据存入缓存

    参数:
        key: 缓存键
        data: 要缓存的数据

    存储格式:
    {
        key: (data, timestamp)
    }
    """
    _cache[key] = (data, time.time())


def _attach_db_ids(items: List[dict], db: Session) -> List[dict]:
    """
    为搜索结果附加数据库 ID

    参数:
        items: 搜索结果列表（来自向量搜索，无数据库 ID）
        db: 数据库会话

    返回:
        附加了 id 字段的结果列表

    工作原理:
    - 向量搜索结果只有 title/content/source/category
    - 需要通过 title 匹配数据库记录获取 id
    - 匹配失败的记录 id 设为 0

    使用场景:
    - 语义搜索结果需要跳转到详情页
    - 前端需要 id 来构造详情页 URL
    """
    if not items:
        return items

    # 提取所有标题
    titles = [it["title"] for it in items]

    # 批量查询数据库，获取标题对应的 ID
    records = (
        db.query(KnowledgeBase.id, KnowledgeBase.title)
        .filter(KnowledgeBase.title.in_(titles))
        .all()
    )

    # 构建标题 -> ID 的映射
    id_map = {title: kid for kid, title in records}

    # 为每个结果附加 ID
    for item in items:
        item["id"] = id_map.get(item["title"], 0)

    return items


def list_knowledge(
    db: Session,
    category: Optional[str] = None,
    page: int = 1,
    page_size: int = 20,
) -> Tuple[List[dict], int]:
    """
    获取知识文章列表

    参数:
        db: 数据库会话
        category: 可选的分类筛选
        page: 页码，从 1 开始
        page_size: 每页数量

    返回:
        (文章列表, 总记录数)

    文章列表结构:
    [
        {
            "id": int,
            "title": str,
            "content": str,  # 截取前 200 字符
            "source": str,
            "category": str
        },
        ...
    ]

    缓存策略:
    - 缓存键: "list:{category}:{page}:{page_size}"
    - 缓存时间: 5 分钟
    - 注意: total 不缓存，每次都查询（数据可能变化）
    """
    # 构造缓存键
    cache_key = f"list:{category}:{page}:{page_size}"

    # 尝试从缓存获取
    cached = _cache_get(cache_key)
    if cached:
        # 缓存命中，但仍需查询 total（数据可能变化）
        total = db.query(KnowledgeBase).filter(
            KnowledgeBase.category == category if category else True
        ).count()
        return cached, total

    # 缓存未命中，查询数据库
    q = db.query(KnowledgeBase)
    if category:
        q = q.filter(KnowledgeBase.category == category)

    # 查询总数
    total = q.count()

    # 分页查询
    items = (
        q.order_by(KnowledgeBase.id)
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )

    # 格式化结果
    result = [
        {
            "id": k.id,
            "title": k.title,
            "content": k.content[:200] + ("..." if len(k.content) > 200 else ""),
            "source": k.source,
            "category": k.category,
        }
        for k in items
    ]

    # 存入缓存
    _cache_set(cache_key, result)

    return result, total


def get_knowledge_detail(db: Session, kid: int) -> Optional[dict]:
    """
    获取知识文章详情

    参数:
        db: 数据库会话
        kid: 文章 ID

    返回:
        文章详情字典，不存在返回 None

    返回结构:
    {
        "id": int,
        "title": str,
        "content": str,  # 完整内容
        "source": str,
        "category": str
    }

    缓存策略:
    - 缓存键: "detail:{kid}"
    - 缓存时间: 5 分钟
    """
    # 构造缓存键
    cache_key = f"detail:{kid}"

    # 尝试从缓存获取
    cached = _cache_get(cache_key)
    if cached:
        return cached[0] if cached else None

    # 缓存未命中，查询数据库
    k = db.query(KnowledgeBase).filter(KnowledgeBase.id == kid).first()
    if not k:
        return None

    # 格式化结果
    result = {
        "id": k.id,
        "title": k.title,
        "content": k.content,  # 完整内容，不截断
        "source": k.source,
        "category": k.category,
    }

    # 存入缓存
    _cache_set(cache_key, [result])

    return result


def search_knowledge(
    query: str,
    page: int = 1,
    page_size: int = 10,
    db: Optional[Session] = None,
) -> List[dict]:
    """
    语义搜索知识文章

    参数:
        query: 搜索关键词
        page: 页码，从 1 开始
        page_size: 每页数量
        db: 可选的数据库会话（用于降级搜索）

    返回:
        搜索结果列表

    搜索结果结构:
    [
        {
            "title": str,
            "content": str,  # 截取前 200 字符
            "source": str,
            "category": str,
            "score": float,  # 相似度分数
            "id": int        # 数据库 ID（可能为 0）
        },
        ...
    ]

    搜索策略:
    1. 优先使用向量语义搜索（FAISS）
    2. 如果向量搜索无结果且有数据库会话，降级为模糊搜索
    3. 模糊搜索使用 SQL LIKE 语句

    缓存策略:
    - 缓存键: "search:{query}:{page}:{page_size}"
    - 缓存时间: 5 分钟
    """
    # 构造缓存键
    cache_key = f"search:{query}:{page}:{page_size}"

    # 尝试从缓存获取
    cached = _cache_get(cache_key)
    if cached:
        return cached

    # ========== 1. 向量语义搜索 ==========
    # 调用检索器进行语义搜索
    # top_k 设置为 page_size * 2，预留分页空间
    results = retrieve(query, top_k=min(page_size * 2, 20))

    # ========== 2. 降级为数据库模糊搜索 ==========
    # 如果向量搜索失败或无结果，使用数据库模糊搜索
    if not results and db is not None:
        search_pattern = f"%{query}%"
        items = (
            db.query(KnowledgeBase)
            .filter(
                or_(
                    KnowledgeBase.title.like(search_pattern),
                    KnowledgeBase.content.like(search_pattern)
                )
            )
            .limit(page_size * 2)
            .all()
        )
        results = [
            {
                "title": k.title,
                "content": k.content[:200] + ("..." if len(k.content) > 200 else ""),
                "source": k.source,
                "category": k.category,
                "score": 1.0,  # 模糊搜索分数设为 1.0
            }
            for k in items
        ]

    # ========== 3. 分页处理 ==========
    offset = (page - 1) * page_size
    paginated = results[offset:offset + page_size]

    # ========== 4. 附加数据库 ID ==========
    # 向量搜索结果不带数据库 ID，需要通过标题匹配
    if db:
        paginated = _attach_db_ids(paginated, db)

    # ========== 5. 存入缓存 ==========
    _cache_set(cache_key, paginated)

    return paginated
