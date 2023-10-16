from ultralytics import YOLO


def load_model() -> YOLO:
    """
    Loads the pretrained model from the weights folder
    :return: model
    """

    model = YOLO('../weights/detector.pt')

    model.fuse()

    return model
