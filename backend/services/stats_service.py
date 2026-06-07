from datetime import datetime, timedelta
from typing import List
from sqlalchemy import func, extract
from sqlalchemy.orm import Session
from backend.models.record import RecognitionRecord
from backend.models.user import User


def get_recognition_stats(db: Session, openid: str) -> dict:
    """获取用户识别统计数据"""
    user = db.query(User).filter(User.openid == openid).first()
    if not user:
        return {
            "total": 0,
            "normal_count": 0,
            "abnormal_count": 0,
            "monthly": [],
            "by_task": [],
        }

    records = db.query(RecognitionRecord).filter(
        RecognitionRecord.user_id == user.id
    ).all()

    total = len(records)
    normal_keywords = ["正常", "品质", "优", "合格", "good"]
    normal_count = sum(
        1 for r in records
        if any(kw in (r.result or "") for kw in normal_keywords)
    )
    abnormal_count = total - normal_count

    # 按月份统计（最近6个月）
    six_months_ago = datetime.now() - timedelta(days=180)
    monthly_data: List[dict] = []
    for i in range(6):
        month_start = (datetime.now().replace(day=1) - timedelta(days=30 * i))
        month_start = month_start.replace(day=1)
        if i > 0:
            prev_month = month_start - timedelta(days=1)
            prev_month = prev_month.replace(day=1)
            month_end = month_start
        else:
            month_end = datetime.now() + timedelta(days=1)
        count = db.query(RecognitionRecord).filter(
            RecognitionRecord.user_id == user.id,
            RecognitionRecord.create_time >= month_start,
            RecognitionRecord.create_time < month_end,
        ).count()
        month_data = month_start.strftime("%Y-%m")
        month_label = month_start.strftime("%m月")
        monthly_data.insert(0, {"month": month_label, "count": count, "raw": month_data})

    # 按任务类型统计
    task_counts = db.query(
        RecognitionRecord.task_type,
        func.count(RecognitionRecord.id).label("count")
    ).filter(
        RecognitionRecord.user_id == user.id
    ).group_by(RecognitionRecord.task_type).all()

    task_labels = {
        "disease": "病虫害",
        "grade": "质量分级",
        "quality": "品质识别",
    }
    by_task = [
        {
            "task": task_labels.get(tc[0] or "other", tc[0] or "其他"),
            "count": tc[1],
        }
        for tc in task_counts
    ]

    return {
        "total": total,
        "normal_count": normal_count,
        "abnormal_count": abnormal_count,
        "monthly": monthly_data,
        "by_task": by_task,
    }
