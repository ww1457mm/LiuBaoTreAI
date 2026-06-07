from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.database.mysql import get_db
from backend.services import region_service

router = APIRouter(prefix="/api", tags=["region"])


@router.get("/regions")
def get_regions(db: Session = Depends(get_db)):
    """获取梧州六堡茶所有产区列表"""
    regions = region_service.list_regions(db)
    return {
        "code": 0,
        "data": regions,
        "total": len(regions),
    }


@router.get("/regions/{rid}")
def get_region_detail(rid: int, db: Session = Depends(get_db)):
    """获取单个产区详细信息"""
    region = region_service.get_region_by_id(db, rid)
    if not region:
        raise HTTPException(404, "产区不存在")
    return {"code": 0, "data": region}
