from ultralytics import YOLO

if __name__=="__main__":
    model=YOLO(r"yolo11n.pt")#加载模型，可更改加载的模型，如yolo11n-cls或者yolo8模型
    model.train(
        data=r"traffic_dataset.yaml",#训练coco8的数据集,可更换为其它的数据集，在cfg-dataset中可进行选择
        epochs=100,#训练轮数
        batch=-1,#一个批次训练16张图片，batch增大，训练效率提高，显存占有率高，但有上限，可设置为-1，运行得出最佳batch数
        imgsz=640,#值越小，训练越快，适合最好，图大目标小，建议设大，能使图片更清晰
        workers=8,
        cache="ram",#不使用缓存，用内存设置为“ram”，把图片先加载进内存里，进行缩放，再喂给模型
        #amp=False,
        #device='cpu'让GPU来跑
    )