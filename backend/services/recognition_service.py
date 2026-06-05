import uuid
from pathlib import Path

from ai_models.yolo.predict import predict_image

UPLOAD_DIR = Path(__file__).resolve().parents[1] / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


def save_and_recognize(file_bytes: bytes, filename: str, task: str = "variety") -> dict:
    ext = Path(filename).suffix or ".jpg"
    save_name = f"{uuid.uuid4().hex}{ext}"
    save_path = UPLOAD_DIR / save_name
    save_path.write_bytes(file_bytes)
    result = predict_image(str(save_path), task=task)
    result["image_url"] = f"/uploads/{save_name}"
    result["local_path"] = str(save_path)
    return result
