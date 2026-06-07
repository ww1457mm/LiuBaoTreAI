import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from backend.database.mysql import Base, engine, SessionLocal
from backend.models.user import User
from backend.models.record import RecognitionRecord, QARecord, Favorite
from backend.models.knowledge import KnowledgeBase
from backend.models.region import Region
from backend.models.journal import TeaJournal
from backend.models.quiz import QuizRecord


def _import_knowledge_base(db):
    """导入知识库数据"""
    if db.query(KnowledgeBase).count() > 0:
        print(f"知识库数据已存在 ({db.query(KnowledgeBase).count()} 条)")
        return

    kb_root = ROOT / "knowledge_base"
    count = 0
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
        count += 1
    db.commit()
    print(f"知识库数据已导入 {count} 条")


def _import_regions(db):
    """导入产区数据"""
    if db.query(Region).count() > 0:
        print(f"产区数据已存在 ({db.query(Region).count()} 条)")
        return

    regions_data = [
        Region(
            name="六堡镇核心区",
            location="梧州市苍梧县",
            latitude=23.52,
            longitude=111.31,
            description="六堡茶发源地，享有茶乡美誉，是六堡茶最核心产区。六堡镇位于苍梧县西北部，群山环抱，溪流纵横，独特的地理环境和气候条件造就了六堡茶独特的品质。",
            brands="苍松茶厂|梧州茶厂|茂圣茶业",
            harvest_season="春茶3-4月，秋茶9-10月",
            yield_volume="约500吨/年",
            characteristic="汤色红浓，槟榔香显著，回甘持久",
            level=1,
        ),
        Region(
            name="狮寨产区",
            location="梧州市苍梧县狮寨镇",
            latitude=23.58,
            longitude=111.28,
            description="狮寨镇地处六堡茶产区腹地，生态环境优越，森林覆盖率高，云雾缭绕，土壤肥沃，是优质六堡茶的重要产地。",
            brands="六堡茶狮寨合作社",
            harvest_season="春茶4月，秋茶9月",
            yield_volume="约120吨/年",
            characteristic="口感醇厚，香气清幽，山野气韵足",
            level=2,
        ),
        Region(
            name="梨木产区",
            location="梧州市苍梧县梨木镇",
            latitude=23.61,
            longitude=111.35,
            description="梨木镇六堡茶种植面积稳步扩大，近年来注重生态茶园建设，品质优良，逐渐成为六堡茶重要产区之一。",
            brands="梨木茶业",
            harvest_season="春茶4月",
            yield_volume="约80吨/年",
            characteristic="滋味浓醇，甘甜回甘，耐泡度高",
            level=2,
        ),
        Region(
            name="沙头产区",
            location="梧州市苍梧县沙头镇",
            latitude=23.47,
            longitude=111.26,
            description="沙头镇为六堡茶重要扩展产区，近年发展迅速，茶园面积不断扩大，已成为梧州六堡茶产业的重要组成部分。",
            brands="沙头六堡茶合作社",
            harvest_season="春茶3-4月",
            yield_volume="约100吨/年",
            characteristic="茶汤红亮，滋味醇和，适口性好",
            level=2,
        ),
        Region(
            name="岑溪产区",
            location="梧州市岑溪市",
            latitude=22.92,
            longitude=110.99,
            description="梧州岑溪市为六堡茶新兴产区，依托优越的自然条件，茶园面积持续扩大，产量逐年提升，品质稳步提高。",
            brands="岑山茶业|天龙红茶",
            harvest_season="春茶4月，秋茶9月",
            yield_volume="约200吨/年",
            characteristic="香气浓郁，滋味甘醇，汤质饱满",
            level=2,
        ),
        Region(
            name="藤县产区",
            location="梧州市藤县",
            latitude=23.38,
            longitude=110.90,
            description="藤县六堡茶种植规模大，历史悠久，茶叶品质稳定，是梧州六堡茶的重要生产基地之一。",
            brands="藤州茶业",
            harvest_season="春茶4月",
            yield_volume="约180吨/年",
            characteristic="汤色红浓，滋味醇厚，陈香初显",
            level=2,
        ),
        Region(
            name="蒙山产区",
            location="梧州市蒙山县",
            latitude=24.14,
            longitude=110.52,
            description="蒙山县生态资源丰富，海拔较高，云雾多，昼夜温差大，适合发展高山六堡茶，所产茶叶品质独特。",
            brands="蒙山茶业",
            harvest_season="春茶4-5月",
            yield_volume="约90吨/年",
            characteristic="高山茶韵，香高味浓，回甘强烈",
            level=3,
        ),
    ]
    for r in regions_data:
        db.add(r)
    db.commit()
    print(f"产区数据已导入 {len(regions_data)} 条")


def init_database(force_reimport=False):
    """初始化数据库并导入种子数据

    Args:
        force_reimport: 强制重新导入数据（清空现有数据）
    """
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        if force_reimport:
            print("强制重新导入模式：清空现有数据...")
            db.query(Region).delete()
            db.query(KnowledgeBase).delete()
            db.commit()

        _import_knowledge_base(db)
        _import_regions(db)
    finally:
        db.close()
    print("数据库初始化完成")


if __name__ == "__main__":
    # 支持命令行参数 --force 强制重新导入
    force = "--force" in sys.argv
    init_database(force_reimport=force)
