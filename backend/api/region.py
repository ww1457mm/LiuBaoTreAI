from fastapi import APIRouter, Depends
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
