import io
import uuid
from pathlib import Path
from typing import Tuple

from PIL import Image

from ai_models.yolo.predict import predict_image

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 压缩参数 — 对检测任务保留更高画质
MAX_SIZE = 1280       # 最长边像素（提升以保留病害细节）
QUALITY = 92          # JPEG 质量（提升以减少压缩伪影）


def _compress_image(file_bytes: bytes, filename: str) -> Tuple[bytes, str]:
    """压缩图片，保留足够细节用于病害检测。"""
    try:
        img = Image.open(io.BytesIO(file_bytes))
        original_format = img.format or "JPEG"
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        w, h = img.size
        if max(w, h) > MAX_SIZE:
            ratio = MAX_SIZE / max(w, h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        output = io.BytesIO()
        output_format = "JPEG" if original_format in ("JPEG", "JPG") else "PNG"
        ext = ".jpg" if output_format == "JPEG" else ".png"
        img.save(output, format=output_format, quality=QUALITY, optimize=True)
        return output.getvalue(), ext
    except Exception:
        return file_bytes, Path(filename).suffix or ".jpg"


def save_and_recognize(file_bytes: bytes, filename: str, task: str = "disease") -> dict:
    compressed_bytes, ext = _compress_image(file_bytes, filename)
    save_name = f"{uuid.uuid4().hex}{ext}"
    save_path = UPLOAD_DIR / save_name
    save_path.write_bytes(compressed_bytes)

    result = predict_image(str(save_path), task=task)
    result["image_url"] = f"/uploads/{save_name}"
    result["local_path"] = str(save_path)
    return result