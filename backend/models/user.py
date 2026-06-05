from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from backend.database.mysql import Base


class User(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, autoincrement=True)
    openid = Column(String(64), unique=True, nullable=False, index=True)
    nickname = Column(String(64), default="茶友")
    avatar = Column(String(512), default="")
    create_time = Column(DateTime, server_default=func.now())
