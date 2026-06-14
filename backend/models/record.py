"""
记录数据模型 - 存储用户操作记录

包含三个表：
1. recognition_record: 图像识别记录
2. qa_record: 问答记录
3. favorite: 收藏记录

这些表都与 user 表关联（通过 user_id 外键）
"""

from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database.mysql import Base


class RecognitionRecord(Base):
    """
    图像识别记录表

    表名: recognition_record

    存储用户使用图像识别功能的记录，包括：
    - 上传的图片 URL
    - 识别结果（如茶叶品种）
    - 置信度
    - 描述和建议

    字段说明:
    - id: 主键
    - user_id: 关联用户 ID（外键）
    - image_url: 上传的图片地址
    - result: 识别结果（如 "六堡茶"）
    - confidence: 置信度（如 "0.95"）
    - description: 详细描述
    - suggestion: 建议（如冲泡方法）
    - task_type: 任务类型（variety=品种识别, quality=品质鉴定）
    - create_time: 创建时间（自动填充）
    """
    __tablename__ = "recognition_record"

    # 主键 ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 关联用户 ID，建立索引加速查询
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    # 上传的图片 URL
    image_url = Column(String(512), nullable=False)

    # 识别结果，如 "六堡茶", "普洱茶"
    result = Column(String(128), nullable=False)

    # 置信度，存储为字符串，如 "0.95"
    confidence = Column(String(32), default="0")

    # 详细描述
    description = Column(Text, default="")

    # 建议，如冲泡方法、存储建议
    suggestion = Column(Text, default="")

    # 任务类型：variety=品种识别, quality=品质鉴定
    task_type = Column(String(32), default="variety")

    # 创建时间，数据库自动填充
    create_time = Column(DateTime, server_default=func.now())


class QARecord(Base):
    """
    问答记录表

    表名: qa_record

    存储用户与 AI 的问答记录，包括：
    - 用户问题
    - AI 回答
    - 参考资料（JSON 格式）

    字段说明:
    - id: 主键
    - user_id: 关联用户 ID（外键）
    - question: 用户问题
    - answer: AI 回答
    - references_json: 参考资料 JSON 字符串
    - create_time: 创建时间（自动填充）

    references_json 格式:
    [
        {
            "title": "冲泡方法",
            "content": "...",
            "source": "knowledge_base/brew/冲泡方法.txt",
            "category": "brew",
            "score": 0.8523
        },
        ...
    ]
    """
    __tablename__ = "qa_record"

    # 主键 ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 关联用户 ID
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    # 用户问题
    question = Column(Text, nullable=False)

    # AI 回答
    answer = Column(Text, nullable=False)

    # 参考资料 JSON 字符串，存储检索到的知识块
    references_json = Column(Text, default="[]")

    # 创建时间
    create_time = Column(DateTime, server_default=func.now())


class Favorite(Base):
    """
    收藏表

    表名: favorite

    存储用户的收藏记录，支持三种类型：
    - knowledge: 知识文章收藏
    - qa: 问答记录收藏
    - recognition: 识别记录收藏

    字段说明:
    - id: 主键
    - user_id: 关联用户 ID（外键）
    - fav_type: 收藏类型（knowledge/qa/recognition）
    - target_id: 关联的目标 ID（如文章 ID、问答记录 ID）
    - title: 收藏标题
    - content: 收藏内容
    - create_time: 创建时间（自动填充）

    使用场景:
    - 用户收藏感兴趣的知识文章
    - 用户收藏有价值的问答记录
    - 用户收藏识别结果
    """
    __tablename__ = "favorite"

    # 主键 ID
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 关联用户 ID
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)

    # 收藏类型：knowledge=知识文章, qa=问答记录, recognition=识别记录
    fav_type = Column(String(32), nullable=False)

    # 关联的目标 ID，0 表示无关联
    target_id = Column(Integer, default=0)

    # 收藏标题
    title = Column(String(256), default="")

    # 收藏内容
    content = Column(Text, default="")

    # 创建时间
    create_time = Column(DateTime, server_default=func.now())
