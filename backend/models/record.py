from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func
from backend.database.mysql import Base


class RecognitionRecord(Base):
    __tablename__ = "recognition_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    image_url = Column(String(512), nullable=False)
    result = Column(String(128), nullable=False)
    confidence = Column(String(32), default="0")
    description = Column(Text, default="")
    suggestion = Column(Text, default="")
    task_type = Column(String(32), default="variety")
    create_time = Column(DateTime, server_default=func.now())


class QARecord(Base):
    __tablename__ = "qa_record"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    question = Column(Text, nullable=False)
    answer = Column(Text, nullable=False)
    references_json = Column(Text, default="[]")
    create_time = Column(DateTime, server_default=func.now())


class Favorite(Base):
    __tablename__ = "favorite"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, index=True)
    fav_type = Column(String(32), nullable=False)  # knowledge | qa | recognition
    target_id = Column(Integer, default=0)
    title = Column(String(256), default="")
    content = Column(Text, default="")
    create_time = Column(DateTime, server_default=func.now())
