from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

MODEL_PATH = Path(__file__).parent / "best.pt"

# 演示类别（训练模型不存在时使用）
DEMO_CLASSES = {
    "variety": [
        ("传统六堡茶", 0.92, "条索紧结、色泽黑褐，具有典型六堡茶外形特征。", "建议按标准工艺冲泡品饮。"),
        ("现代工艺六堡", 0.85, "外形匀整，发酵程度适中。", "适合日常品饮，注意醒茶。"),
    ],
    "grade": [
        ("特级", 0.88, "芽叶细嫩，金毫显露，品质上乘。", "宜低温慢泡，细品其醇。"),
        ("一级", 0.82, "条索尚紧，汤色红浓。", "可长期存放陈化。"),
        ("二级", 0.76, "叶片稍粗，性价比高。", "适合煮饮或日常饮用。"),
    ],
    "disease": [
        ("健康茶叶", 0.91, "叶片完整，无霉变、虫蛀迹象。", "存储于干燥通风处即可。"),
        ("轻微受潮", 0.68, "叶色略暗，可能有潮气。", "建议摊晾除湿后尽快饮用。"),
        ("白霜菌花", 0.75, "表面可见菌花，属陈化正常现象。", "洗茶后品饮，无需担心。"),
    ],
}


def predict_image(image_path: str, task: str = "variety") -> dict:
    """YOLOv8 推理；无模型文件时返回演示结果。"""
    if MODEL_PATH.exists():
        try:
            return _yolo_predict(image_path, task)
        except Exception:
            pass
    return _demo_predict(task)


def _yolo_predict(image_path: str, task: str) -> dict:
    from ultralytics import YOLO

    model = YOLO(str(MODEL_PATH))
    results = model(image_path, verbose=False)[0]
    if not results.boxes or len(results.boxes) == 0:
        return _demo_predict(task)
    box = results.boxes[0]
    cls_id = int(box.cls[0])
    conf = float(box.conf[0])
    name = results.names.get(cls_id, "未知类别")
    return {
        "category": name,
        "confidence": round(conf, 4),
        "description": f"模型识别为：{name}",
        "suggestion": "请结合专业品鉴进一步确认。",
        "task": task,
    }


def _demo_predict(task: str) -> dict:
    options = DEMO_CLASSES.get(task, DEMO_CLASSES["variety"])
    name, conf, desc, suggestion = options[0]
    return {
        "category": name,
        "confidence": conf,
        "description": desc + "（演示模式：请放置 best.pt 以启用真实识别）",
        "suggestion": suggestion,
        "task": task,
    }
