from typing import List
from sqlalchemy.orm import Session
from backend.models.region import Region


def list_regions(db: Session) -> List[dict]:
    """获取所有产区列表，按 level 排序（核心区优先）"""
    regions = db.query(Region).order_by(Region.level, Region.id).all()
    return [_region_to_dict(r) for r in regions]


def get_region_by_id(db: Session, rid: int) -> dict | None:
    region = db.query(Region).filter(Region.id == rid).first()
    if not region:
        return None
    return _region_to_dict(region)


def _region_to_dict(r: Region) -> dict:
    return {
        "id": r.id,
        "name": r.name,
        "location": r.location,
        "latitude": r.latitude,
        "longitude": r.longitude,
        "description": r.description or "",
        "brands": r.brands.split("|") if r.brands else [],
        "harvest_season": r.harvest_season or "",
        "yield_volume": r.yield_volume or "",
        "characteristic": r.characteristic or "",
        "level": r.level,
    }
