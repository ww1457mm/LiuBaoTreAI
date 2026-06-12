import io
import uuid
from pathlib import Path
from typing import Tuple

from PIL import Image

from ai_models.yolo.predict import predict_image

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# 压缩参数
MAX_SIZE = 1024       # 最长边像素
QUALITY = 85         # JPEG 质量
THUMBNAIL_SIZE = (256, 256)  # 缩略图尺寸


def _compress_image(file_bytes: bytes, filename: str) -> Tuple[bytes, str]:
    """压缩图片到合理尺寸，返回（压缩后字节, 目标扩展名）。"""
    try:
        img = Image.open(io.BytesIO(file_bytes))
        original_format = img.format or "JPEG"
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        # 按最长边缩放
        w, h = img.size
        if max(w, h) > MAX_SIZE:
            ratio = MAX_SIZE / max(w, h)
            new_w, new_h = int(w * ratio), int(h * ratio)
            img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        output = io.BytesIO()
        output_format = "JPEG" if original_format == "JPEG" else "PNG"
        ext = ".jpg" if output_format == "JPEG" else ".png"
        img.save(output, format=output_format, quality=QUALITY, optimize=True)
        return output.getvalue(), ext
    except Exception:
        # 压缩失败直接返回原图
        return file_bytes, Path(filename).suffix or ".jpg"


def save_and_recognize(file_bytes: bytes, filename: str, task: str = "variety") -> dict:
    # 先压缩图片
    compressed_bytes, ext = _compress_image(file_bytes, filename)
    save_name = f"{uuid.uuid4().hex}{ext}"
    save_path = UPLOAD_DIR / save_name
    save_path.write_bytes(compressed_bytes)

    print(f"[recognition_service] save_path: {save_path}, exists: {save_path.exists()}, size: {save_path.stat().st_size if save_path.exists() else 0}")

    result = predict_image(str(save_path), task=task)
    print(f"[recognition_service] predict result: {result}")

    result["image_url"] = f"/uploads/{save_name}"
    result["local_path"] = str(save_path)
    return result
