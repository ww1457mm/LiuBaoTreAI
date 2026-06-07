from sqlalchemy import Column, Integer, String, Text, Float
from backend.database.mysql import Base


class Region(Base):
    """六堡茶产区数据模型"""
    __tablename__ = "regions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(64), nullable=False, comment="产区名称")
    location = Column(String(128), nullable=False, comment="所属县市")
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    description = Column(Text, default="", comment="产区描述")
    brands = Column(Text, default="", comment="代表品牌，多个用 | 分隔")
    harvest_season = Column(String(64), default="", comment="采摘时节")
    yield_volume = Column(String(64), default="", comment="年产量")
    characteristic = Column(String(256), default="", comment="品质特点")
    level = Column(Integer, default=1, comment="产区等级：1=核心区，2=主产区，3=一般产区")
