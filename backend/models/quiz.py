from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database.mysql import Base


class QuizRecord(Base):
    """答题记录"""
    __tablename__ = "quiz_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    score = Column(Integer, nullable=False, comment="得分")
    total = Column(Integer, nullable=False, comment="总题数")
    create_time = Column(DateTime, server_default=func.now())
