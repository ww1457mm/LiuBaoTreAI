import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.database.mysql import Base, engine, SessionLocal
from backend.models.user import User
from backend.models.record import RecognitionRecord, QARecord, Favorite
from backend.models.knowledge import KnowledgeBase


def init_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if db.query(KnowledgeBase).count() == 0:
            kb_root = ROOT / "knowledge_base"
            for txt in kb_root.rglob("*.txt"):
                content = txt.read_text(encoding="utf-8").strip()
                if not content:
                    continue
                db.add(
                    KnowledgeBase(
                        title=txt.stem,
                        content=content,
                        source=str(txt.relative_to(ROOT)).replace("\\", "/"),
                        category=txt.parent.name,
                    )
                )
            db.commit()
            print("知识库数据已导入")
    finally:
        db.close()
    print("数据库初始化完成")


if __name__ == "__main__":
    init_database()
