from typing import Generic, List, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """统一分页响应格式。"""

    code: int = 0
    data: List[T] = Field(default_factory=list)
    total: int = 0
    page: int = 1
    page_size: int = 20
    has_more: bool = False


def apply_pagination(query, page: int, page_size: int):
    """
    对 SQLAlchemy 查询对象进行分页，返回 dict 格式结果。
    query: SQLAlchemy query object (未调用 .all())
    page: 页码（从 1 开始）
    page_size: 每页数量
    """
    total = query.count()
    offset = (page - 1) * page_size
    items = query.offset(offset).limit(page_size).all()
    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "has_more": (page * page_size) < total,
    }
