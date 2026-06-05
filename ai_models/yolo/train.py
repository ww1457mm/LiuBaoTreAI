"""YOLOv8 训练脚本：将数据集置于 ai_models/yolo/dataset/ 后运行。"""
from pathlib import Path

DATA_YAML = Path(__file__).parent / "dataset" / "data.yaml"


def main():
    if not DATA_YAML.exists():
        print("请准备 dataset/data.yaml 及标注数据后再训练。")
        return
    from ultralytics import YOLO

    model = YOLO("yolov8n.pt")
    model.train(data=str(DATA_YAML), epochs=50, imgsz=640, project="runs", name="liubao")
    print("训练完成，请将 best.pt 复制到 ai_models/yolo/best.pt")


if __name__ == "__main__":
    main()
