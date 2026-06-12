from __future__ import annotations

from pathlib import Path

MODEL_PATH = Path(__file__).parent / "best.pt"

# 与 best.pt 训练类别一致：0-4、6-7 为病害/虫害，5 为正常茶叶
CLASS_INFO = {
    0: (
        "茶黑腐病",
        "叶片出现黑腐症状，叶色暗褐或发黑，严重时叶片枯死脱落。",
        "加强茶园通风排水，及时清除病叶，必要时使用针对性杀菌剂防治。",
    ),
    1: (
        "茶褐斑病",
        "叶片出现褐色圆形或不规则病斑，边缘清晰，影响光合与品质。",
        "改善茶园通风，降低湿度，发病初期可喷施保护性杀菌剂。",
    ),
    2: (
        "茶落叶病",
        "叶片出现锈斑或落叶病特征，叶脉间变色，严重时提前落叶。",
        "及时摘除病叶，加强肥水管理，必要时进行药剂防治。",
    ),
    3: (
        "红蜘蛛危害",
        "叶片背面可见红蜘蛛或细小白点，叶色失绿、出现灰白斑点。",
        "加强监测，保持茶园湿度，发生时可使用专用杀螨剂防治。",
    ),
    4: (
        "茶小绿叶蝉危害",
        "叶片边缘卷曲、出现焦枯或黄化，为常见虫害特征。",
        "及时采摘嫩梢，清除杂草，必要时使用低毒杀虫剂防治。",
    ),
    6: (
        "茶白星病",
        "叶片出现白色星点状病斑，多从叶尖或叶缘开始扩展。",
        "清除病叶，改善通风，发病期可喷施铜制剂等杀菌剂。",
    ),
    7: (
        "茶叶病害",
        "检测到茶叶病害特征，建议进一步确认具体类型。",
        "隔离病叶，检查同批次茶叶，必要时请专业人员鉴定处理。",
    ),
}

HEALTHY_CLASS_ID = 5  # Tea leaf

HEALTHY_INFO = (
    "未检出明显病害",
    "未检测到明显病害或虫害特征，建议结合实物进一步确认。",
    "若叶片有异常，可换角度、近距离重新拍摄；存储时保持干燥通风。",
)

NO_DETECTION_INFO = (
    "未检出目标",
    "未能从图片中识别到茶叶或病害特征，请重新拍摄。",
    "建议在光线充足、背景简洁的环境下，将茶叶平铺或特写拍摄。",
)

CONF_THRESHOLD = 0.25

_model = None


def _get_model():
    global _model
    if _model is None:
        from ultralytics import YOLO

        _model = YOLO(str(MODEL_PATH))
    return _model


def predict_image(image_path: str, task: str = "disease") -> dict:
    """YOLOv8 病虫害检测；无模型文件时返回演示结果。"""
    print(f"[predict] MODEL_PATH.exists(): {MODEL_PATH.exists()}, path: {MODEL_PATH}")

    if MODEL_PATH.exists():
        try:
            result = _yolo_predict(image_path)
            print(f"[predict] YOLO result: {result}")
            return result
        except Exception as e:
            print(f"[predict] YOLO predict error: {e}")
            import traceback
            traceback.print_exc()
            pass
    return _demo_predict()


def _yolo_predict(image_path: str) -> dict:
    model = _get_model()
    results = model(image_path, verbose=False)[0]
    boxes = results.boxes

    if boxes is None or len(boxes) == 0:
        return _result_from_info(NO_DETECTION_INFO, confidence=0.0)

    disease_candidates = []
    healthy_candidates = []

    for i in range(len(boxes)):
        cls_id = int(boxes.cls[i])
        conf = float(boxes.conf[i])
        if conf < CONF_THRESHOLD:
            continue
        if cls_id == HEALTHY_CLASS_ID:
            healthy_candidates.append(conf)
        else:
            disease_candidates.append((cls_id, conf))

    # 优先返回置信度最高的病害/虫害，避免被“正常茶叶”误判覆盖
    if disease_candidates:
        cls_id, conf = max(disease_candidates, key=lambda item: item[1])
        if cls_id in CLASS_INFO:
            name, desc, suggestion = CLASS_INFO[cls_id]
            return _build_result(name, conf, desc, suggestion)
        label = model.names.get(cls_id, f"类别{cls_id}")
        return _build_result(
            label,
            conf,
            f"检测到「{label}」，请上传更清晰的茶叶图片以便进一步确认。",
            "建议在光线充足、背景简洁的环境下拍摄茶叶图片。",
        )

    if healthy_candidates:
        return _result_from_info(HEALTHY_INFO, confidence=round(max(healthy_candidates), 4))

    return _result_from_info(NO_DETECTION_INFO, confidence=0.0)


def _build_result(category: str, confidence: float, description: str, suggestion: str) -> dict:
    return {
        "category": category,
        "confidence": round(confidence, 4),
        "description": description,
        "suggestion": suggestion,
        "task": "disease",
    }


def _result_from_info(info: tuple[str, str, str], confidence: float) -> dict:
    name, desc, suggestion = info
    return _build_result(name, confidence, desc, suggestion)


def _demo_predict() -> dict:
    name, desc, suggestion = HEALTHY_INFO
    return {
        "category": name,
        "confidence": 0.0,
        "description": desc + "（演示模式：放置 best.pt 以启用真实检测）",
        "suggestion": suggestion,
        "task": "disease",
    }
