from __future__ import annotations

from pathlib import Path

import numpy as np
from PIL import Image

MODEL_PATH = Path(__file__).parent / "best.pt"

CLASS_INFO = {
    0: ("茶黑腐病", "叶片出现黑腐症状，叶色暗褐或发黑，严重时叶片枯死脱落。", "加强茶园通风排水，及时清除病叶，必要时使用针对性杀菌剂防治。"),
    1: ("茶褐斑病", "叶片出现褐色圆形或不规则病斑，边缘清晰，影响光合与品质。", "改善茶园通风，降低湿度，发病初期可喷施保护性杀菌剂。"),
    2: ("茶落叶病", "叶片出现锈斑或落叶病特征，叶脉间变色，严重时提前落叶。", "及时摘除病叶，加强肥水管理，必要时进行药剂防治。"),
    3: ("红蜘蛛危害", "叶片背面可见红蜘蛛或细小白点，叶色失绿、出现灰白斑点。", "加强监测，保持茶园湿度，发生时可使用专用杀螨剂防治。"),
    4: ("茶小绿叶蝉危害", "叶片边缘卷曲、出现焦枯或黄化，为常见虫害特征。", "及时采摘嫩梢，清除杂草，必要时使用低毒杀虫剂防治。"),
    6: ("茶白星病", "叶片出现白色星点状病斑，多从叶尖或叶缘开始扩展。", "清除病叶，改善通风，发病期可喷施铜制剂等杀菌剂。"),
    7: ("茶叶病害", "检测到茶叶病害特征，建议进一步确认具体类型。", "隔离病叶，检查同批次茶叶，必要时请专业人员鉴定处理。"),
}

HEALTHY_CLASS_ID = 5

HEALTHY_INFO = ("未检出明显病害", "未检测到明显病害或虫害特征，茶叶状态正常。", "若叶片确有异常，可换角度、近距离重新拍摄；存储时保持干燥通风。")
NO_DETECTION_INFO = ("未检出茶叶", "未能从图片中识别到茶叶叶片，请确保拍摄对象为茶叶。", "建议在光线充足、背景简洁的环境下，将茶叶平铺或近距离特写拍摄。")
NOT_TEA_LEAF_INFO = ("非茶叶图片", "上传的图片中未检测到茶叶叶片特征，可能不是茶叶照片。", "请拍摄茶叶叶片本身，而非屏幕截图或其他物体。将茶叶放在纯色背景上，从正上方拍摄。")
LOW_CONFIDENCE_INFO = ("识别不确定", "检测到疑似特征但置信度不足，可能与拍摄角度、光线或背景有关。", "建议在自然光下、以纯色背景（白纸）平铺茶叶，从正上方拍摄。")

CONF_THRESHOLD = 0.35
LOW_CONF_THRESHOLD = 0.50

_model = None


def _get_model():
    global _model
    if _model is None:
        from ultralytics import YOLO
        _model = YOLO(str(MODEL_PATH))
    return _model


def _is_likely_tea_leaf(image_path: str) -> bool:
    """叶片颜色预检：判断图片是否可能包含茶叶。

    两步判断：
    1. 满幅叶片（绿色连续块占比高）→ 直接通过
    2. 白底叶片（非白像素中绿色/褐色主导）→ 通过
    3. 其他（UI 截图等杂色主导）→ 拒绝
    """
    try:
        img = Image.open(image_path).convert("RGB")
        w, h = img.size
        if max(w, h) > 256:
            ratio = 256 / max(w, h)
            img = img.resize((int(w * ratio), int(h * ratio)), Image.Resampling.LANCZOS)
        arr = np.array(img, dtype=np.float32)
        total = arr.shape[0] * arr.shape[1]
        r, g, b = arr[:, :, 0], arr[:, :, 1], arr[:, :, 2]

        # 绿色连续块：16x16 网格中绿色主导的块占比
        green_mask = (g > r) & (g > b) & (g > 35)
        block_sz = 16
        green_blocks = 0
        total_blocks = 0
        for y in range(0, arr.shape[0], block_sz):
            for x in range(0, arr.shape[1], block_sz):
                blk = green_mask[y:y+block_sz, x:x+block_sz]
                if blk.size > 0:
                    total_blocks += 1
                    if blk.sum() / blk.size > 0.45:
                        green_blocks += 1
        green_block_ratio = green_blocks / max(total_blocks, 1)

        # 满幅叶片 → 直接通过
        if green_block_ratio > 0.50:
            return True

        # 非白色像素中，叶片颜色占比
        non_white = ~((r > 210) & (g > 210) & (b > 210))
        nw_count = non_white.sum()
        if nw_count < total * 0.03:  # 几乎全是白色 → 拒绝
            return False

        nw_r, nw_g, nw_b = r[non_white], g[non_white], b[non_white]
        leaf_like = ((nw_g > nw_r) & (nw_g > nw_b)) | ((nw_r > nw_b) & (nw_g > nw_b) & (nw_r < 200) & (nw_g > 40))
        leaf_ratio = leaf_like.sum() / nw_count

        # 非白区中叶色主导 → 白底茶叶
        if leaf_ratio > 0.45:
            return True

        return False
    except Exception:
        return True  # 预检失败时放行，让 YOLO 兜底


def predict_image(image_path: str, task: str = "disease") -> dict:
    if not MODEL_PATH.exists():
        return {"category": "模型未加载", "confidence": 0.0, "description": "检测模型文件缺失，请放置 best.pt 到 ai_models/yolo/ 目录后重启服务。", "suggestion": "确认 best.pt 文件存在且完整（约 6MB）。", "task": task}

    if not _is_likely_tea_leaf(image_path):
        return _result_from_info(NOT_TEA_LEAF_INFO, confidence=0.0)

    try:
        return _yolo_predict(image_path)
    except Exception:
        return _result_from_info(NO_DETECTION_INFO, confidence=0.0)


def _yolo_predict(image_path: str) -> dict:
    model = _get_model()
    results = model(image_path, verbose=False)[0]
    boxes = results.boxes

    if boxes is None or len(boxes) == 0:
        return _result_from_info(NO_DETECTION_INFO, confidence=0.0)

    disease_detections = {}
    healthy_confs = []

    for i in range(len(boxes)):
        cls_id = int(boxes.cls[i])
        conf = float(boxes.conf[i])
        if conf < CONF_THRESHOLD:
            continue
        if cls_id == HEALTHY_CLASS_ID:
            healthy_confs.append(conf)
        else:
            if cls_id not in disease_detections or conf > disease_detections[cls_id]:
                disease_detections[cls_id] = conf

    if disease_detections:
        best_cls = max(disease_detections, key=disease_detections.get)
        best_conf = disease_detections[best_cls]
        if best_conf < LOW_CONF_THRESHOLD:
            return _result_from_info(LOW_CONFIDENCE_INFO, confidence=round(best_conf, 4))
        if best_cls in CLASS_INFO:
            name, desc, suggestion = CLASS_INFO[best_cls]
            return _build_result(name, best_conf, desc, suggestion)
        label = model.names.get(best_cls, f"class_{best_cls}")
        return _build_result(label, best_conf, f"检测到「{label}」。", "在光线充足、背景简洁的环境下拍摄。")

    if healthy_confs:
        return _result_from_info(HEALTHY_INFO, confidence=round(max(healthy_confs), 4))

    return _result_from_info(NO_DETECTION_INFO, confidence=0.0)


def _build_result(category: str, confidence: float, description: str, suggestion: str) -> dict:
    return {"category": category, "confidence": round(confidence, 4), "description": description, "suggestion": suggestion, "task": "disease"}


def _result_from_info(info: tuple[str, str, str], confidence: float) -> dict:
    name, desc, suggestion = info
    return _build_result(name, confidence, desc, suggestion)