"""
知识库 API 模块 - 提供知识文章的查询和搜索接口

API 端点：
- GET /api/knowledge: 获取知识文章列表（支持分类筛选和分页）
- GET /api/knowledge/search/query: 语义搜索知识文章
- GET /api/knowledge/{kid}: 获取单篇文章详情

功能特点：
- 分类筛选：按历史文化、制作工艺、冲泡存储等分类
- 分页查询：支持自定义页码和每页数量
- 语义搜索：基于向量检索的智能搜索
- 降级策略：向量搜索失败时降级为数据库模糊搜索
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from backend.database.mysql import get_db
from backend.services import knowledge_service

# 创建路由器
router = APIRouter(prefix="/api", tags=["knowledge"])


@router.get("/knowledge")
def get_knowledge_list(
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    """
    获取知识文章列表

    参数:
        category: 可选的分类筛选（如 "history", "process", "brew"）
        page: 页码，从 1 开始，默认 1
        page_size: 每页数量，范围 [1, 100]，默认 20
        db: 数据库会话（依赖注入）

    返回:
        JSON 响应:
        {
            "code": 0,
            "data": [
                {
                    "id": int,
                    "title": str,
                    "content": str,  # 截取前 200 字符
                    "source": str,
                    "category": str
                },
                ...
            ],
            "total": int,       # 总记录数
            "page": int,        # 当前页码
            "page_size": int,   # 每页数量
            "has_more": bool    # 是否有下一页
        }

    使用场景:
    - 知识库首页展示文章列表
    - 按分类筛选文章
    - 分页浏览
    """
    items, total = knowledge_service.list_knowledge(
        db, category=category, page=page, page_size=page_size
    )
    return {
        "code": 0,
        "data": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": (page * page_size) < total,
    }


@router.get("/knowledge/search/query")
def search_knowledge(
    q: str = Query(..., min_length=1, max_length=200),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_db),
):
    """
    语义搜索知识文章

    参数:
        q: 搜索关键词，长度 1-200 字符
        page: 页码，从 1 开始，默认 1
        page_size: 每页数量，范围 [1, 50]，默认 10
        db: 数据库会话（依赖注入）

    返回:
        JSON 响应:
        {
            "code": 0,
            "data": [
                {
                    "title": str,
                    "content": str,
                    "source": str,
                    "category": str,
                    "score": float,  # 相似度分数
                    "id": int        # 数据库 ID（可能为 0）
                },
                ...
            ]
        }

    搜索策略:
    1. 优先使用向量语义搜索（FAISS）
    2. 如果向量搜索无结果，降级为数据库模糊搜索（LIKE）
    3. 结果按相似度排序

    使用场景:
    - 用户输入关键词搜索知识
    - 智能问答的参考资料检索
    """
    items = knowledge_service.search_knowledge(q, page=page, page_size=page_size, db=db)
    return {"code": 0, "data": items}


@router.get("/knowledge/{kid}")
def get_knowledge_detail(kid: int, db: Session = Depends(get_db)):
    """
    获取知识文章详情

    参数:
        kid: 文章 ID
        db: 数据库会话（依赖注入）

    返回:
        JSON 响应:
        {
            "code": 0,
            "data": {
                "id": int,
                "title": str,
                "content": str,  # 完整内容
                "source": str,
                "category": str
            }
        }

    异常:
        404: 文章不存在

    使用场景:
    - 用户点击文章查看详情
    - 展示完整的知识内容
    """
    item = knowledge_service.get_knowledge_detail(db, kid)
    if not item:
        raise HTTPException(404, "文章不存在")
    return {"code": 0, "data": item}
