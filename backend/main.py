import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv

    load_dotenv(ROOT / "backend" / ".env")
    load_dotenv(ROOT / ".env")
except ImportError:
    pass

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api import chat, history, knowledge, recognition, user, region, process, journal, quiz, valuation, recommend
from backend.database.init_db import init_database
from backend.middleware import (
    RateLimitMiddleware,
    RequestLoggingMiddleware,
    register_exception_handlers,
)
from backend.utils.logging_config import logger

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("六堡茶智能服务平台启动中...")
    init_database()
    try:
        from ai_models.rag.vector_store import VectorStore

        VectorStore().build_if_needed()
        logger.info("RAG 向量索引构建完成")
    except Exception as e:
        logger.warning(f"RAG 索引构建跳过: {e}")
    logger.info("启动完成，API 文档地址: /docs")
    yield
    logger.info("六堡茶智能服务平台关闭")


app = FastAPI(
    title="六堡茶智能服务平台",
    description="六堡茶品种识别、问答助手与知识库查询 API",
    version="1.0.0",
    lifespan=lifespan,
)

# 注意：生产环境应限制 allow_origins 为实际域名
# 微信小程序原生请求不受 CORS 限制，但 Swagger UI (/docs) 需要
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RateLimitMiddleware, requests_per_minute=60, burst_size=10)
app.add_middleware(RequestLoggingMiddleware)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(user.router)
app.include_router(recognition.router)
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(history.router)
app.include_router(region.router)
app.include_router(process.router)
app.include_router(journal.router)
app.include_router(quiz.router)
app.include_router(valuation.router)
app.include_router(recommend.router)

register_exception_handlers(app)


@app.get("/")
def root():
    return {
        "message": "六堡茶智能服务平台 API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health")
def health():
    from sqlalchemy import text
    from backend.database.mysql import engine

    db_ok = True
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        db_ok = False

    return {
        "status": "ok" if db_ok else "degraded",
        "service": "liubao-tea",
        "database": "connected" if db_ok else "disconnected",
    }
