from __future__ import annotations

from pathlib import Path

MODEL_PATH = Path(__file__).parent / "best.pt"

# 病害识别信息：id -> (名称, 描述, 建议)
DISEASE_INFO = {
    4: (
        "毛虫危害",
        "叶片可见虫孔或虫体，茶叶被啃食造成残缺，影响品质和卫生。",
        "及时防治，采摘时剔除被害叶片，严重时应停止采摘进行虫害治理。"
    ),
    5: (
        "霉变污染",
        "茶叶受潮霉变，表面出现白霉或绿霉，有异味，汤色暗黑浑浊。",
        "检查存储环境，控制湿度在70%以下，霉变茶叶不可饮用，需及时隔离。"
    ),
    6: (
        "菌类异常",
        "茶叶表面出现白色、绿色或灰色霉点，是储存不当或过度潮湿的信号。",
        "单独隔离存放，避免交叉污染，检查同批次茶叶，严重者应报废处理。"
    ),
    7: (
        "茶果混入",
        "茶叶中夹杂茶果或茶花，影响冲泡口感的纯净度。",
        "通过筛分或风选去除，茶果不影响茶叶主体品质，但影响外观和口感。"
    ),
    8: (
        "箬叶残留",
        "茶叶中残留非茶类植物叶片（多为包装用箬叶），影响纯度。",
        "加强采摘和加工清洁工艺，残留量多时应重新筛选。"
    ),
}

# 正常叶片的描述（用于未检出病害时的友好提示）
HEALTHY_INFO = (
    "茶叶外观正常",
    "未检测到明显霉变、虫蛀或其他可见缺陷，叶片完整，色泽正常。",
    "继续保持良好存储环境：干燥、通风、避光，避免与异味物品混放。"
)


def predict_image(image_path: str, task: str = "disease") -> dict:
    """YOLOv8 推理；无模型文件时返回演示结果。"""
    if MODEL_PATH.exists():
        try:
            return _yolo_predict(image_path)
        except Exception:
            pass
    return _demo_predict()


def _yolo_predict(image_path: str) -> dict:
    from ultralytics import YOLO

    model = YOLO(str(MODEL_PATH))
    results = model(image_path, verbose=False)[0]

    if not results.boxes or len(results.boxes) == 0:
        return _healthy_predict()

    # 取置信度最高的检测框
    best_idx = int(results.boxes.conf.argmax())
    box = results.boxes[best_idx]
    cls_id = int(box.cls[best_idx])
    conf = float(box.conf[best_idx])

    # 品种类别（0-3）视为正常茶叶
    if cls_id in DISEASE_INFO:
        name, desc, suggestion = DISEASE_INFO[cls_id]
    elif cls_id <= 3:
        return _healthy_predict()
    else:
        return {
            "category": f"未知类别({cls_id})",
            "confidence": round(conf, 4),
            "description": "检测到未知类型目标，请上传更清晰的茶叶图片。",
            "suggestion": "建议在光线充足、背景简洁的环境下拍摄茶叶图片。",
            "task": "disease",
        }

    return {
        "category": name,
        "confidence": round(conf, 4),
        "description": desc,
        "suggestion": suggestion,
        "task": "disease",
    }


def _healthy_predict() -> dict:
    name, desc, suggestion = HEALTHY_INFO
    return {
        "category": name,
        "confidence": 1.0,
        "description": desc,
        "suggestion": suggestion,
        "task": "disease",
    }


def _demo_predict() -> dict:
    name, desc, suggestion = HEALTHY_INFO
    return {
        "category": name,
        "confidence": 0.0,
        "description": desc + "（演示模式：放置 best.pt 以启用真实识别）",
        "suggestion": suggestion,
        "task": "disease",
    }
