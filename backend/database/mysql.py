import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# 数据库 URL：优先从环境变量读取，不允许硬编码密码
# 开发模式默认使用 SQLite，生产使用 MySQL
_use_sqlite = os.getenv("USE_SQLITE", "true").lower() == "true"

if _use_sqlite:
    DATABASE_URL = os.getenv("SQLITE_URL", "sqlite:///./backend/liubao_tea.db")
else:
    # MySQL 模式必须提供 DATABASE_URL 环境变量
    DATABASE_URL = os.getenv("DATABASE_URL", "")
    if not DATABASE_URL:
        raise ValueError(
            "MySQL 模式需要设置 DATABASE_URL 环境变量，"
            "例如: mysql+pymysql://user:password@host:3306/liubao_tea?charset=utf8mb4"
        )

connect_args = {"check_same_thread": False} if "sqlite" in DATABASE_URL else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
