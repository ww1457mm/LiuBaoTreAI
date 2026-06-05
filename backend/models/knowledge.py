from sqlalchemy import Column, Integer, String, Text
from backend.database.mysql import Base


class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(128), nullable=False)
    content = Column(Text, nullable=False)
    source = Column(String(256), default="")
    category = Column(String(64), default="")
