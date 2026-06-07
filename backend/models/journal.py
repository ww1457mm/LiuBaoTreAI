from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.sql import func
from backend.database.mysql import Base


class TeaJournal(Base):
    """品茶日记"""
    __tablename__ = "tea_journal"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    tea_name = Column(String(128), nullable=False, comment="茶名")
    tea_type = Column(String(32), default="", comment="茶类：liubao/shengpu/shupu/black/green/white")
    origin = Column(String(128), default="", comment="产地")
    brew_temp = Column(String(16), default="", comment="水温")
    brew_time = Column(String(16), default="", comment="冲泡时间")
    tea_amount = Column(String(32), default="", comment="投茶量")
    aroma_score = Column(Integer, default=3, comment="香气评分 1-5")
    taste_score = Column(Integer, default=3, comment="口感评分 1-5")
    overall_score = Column(Integer, default=3, comment="综合评分 1-5")
    flavor_notes = Column(String(256), default="", comment="风味标签，逗号分隔")
    notes = Column(Text, default="", comment="品茶笔记")
    image_url = Column(String(512), default="", comment="图片地址")
    create_time = Column(DateTime, server_default=func.now())
