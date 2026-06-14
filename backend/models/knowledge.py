"""
知识库数据模型 - 存储六堡茶知识文章

表名: knowledge_base

字段说明:
- id: 主键，自增
- title: 文章标题，最大 128 字符
- content: 文章内容，TEXT 类型（可存储长文本）
- source: 来源文件路径，最大 256 字符
- category: 分类标签，最大 64 字符

分类说明:
- history: 历史文化
- process: 制作工艺
- brew: 冲泡存储
- health: 健康功效
- culture: 品鉴文化
- grade: 等级品鉴
- origin: 产地分布

使用场景:
- 知识库列表展示
- 知识详情页
- RAG 检索的数据源（与向量索引配合）
"""

from sqlalchemy import Column, Integer, String, Text
from backend.database.mysql import Base


class KnowledgeBase(Base):
    """
    知识库表模型

    存储六堡茶相关的知识文章，用于：
    1. 知识库页面展示
    2. RAG 系统的知识源
    3. 语义搜索的数据基础

    与向量索引的关系:
    - 数据库存储完整的文章内容
    - 向量索引（FAISS）存储文本的向量表示
    - 搜索时通过向量检索找到相关文章，再从数据库获取完整内容
    """
    __tablename__ = "knowledge_base"

    # 主键 ID，自动递增
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 文章标题，NOT NULL
    title = Column(String(128), nullable=False)

    # 文章内容，TEXT 类型支持长文本
    content = Column(Text, nullable=False)

    # 来源文件路径，如 "knowledge_base/history/六堡茶历史.txt"
    source = Column(String(256), default="")

    # 分类标签，如 "history", "process", "brew"
    category = Column(String(64), default="")
