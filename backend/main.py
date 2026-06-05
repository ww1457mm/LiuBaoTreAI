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

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.api import chat, history, knowledge, recognition, user
from backend.database.init_db import init_database

UPLOAD_DIR = Path(__file__).parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="六堡茶智能服务平台", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory=str(UPLOAD_DIR)), name="uploads")

app.include_router(user.router)
app.include_router(recognition.router)
app.include_router(chat.router)
app.include_router(knowledge.router)
app.include_router(history.router)


@app.on_event("startup")
def on_startup():
    init_database()
    try:
        from ai_models.rag.vector_store import VectorStore

        VectorStore().build_if_needed()
    except Exception as e:
        print(f"RAG 索引构建跳过: {e}")


@app.get("/")
def root():
    return {"message": "六堡茶智能服务平台 API", "docs": "/docs"}


@app.get("/health")
def health():
    return {"status": "ok"}
