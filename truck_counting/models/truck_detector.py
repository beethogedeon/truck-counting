from typing import Union

import cv2
import supervision as sv
from pydantic import BaseModel
from torch.cuda import is_available

from truck_counting.loaders import load_model


class DetectorResponse(BaseModel):
    frame: None
    nbTrucks: int


class TruckDetector:

    def __init__(self, source: Union[str, int]):
        self.source = source
        self.model = load_model()
        self.device = 'cuda' if is_available() else 'cpu'
        self.labels = []
        self.CLASS_NAMES_DICT = self.model.model.names
        self.height = 640
        self.width = 640
        self.nbTrucks = 0

        # self.checkline = [(0, self.height * 0.75), (self.width, self.height * 0.75)]
        self.box_annotator = sv.BoxAnnotator(sv.ColorPalette.default(), thickness=3, text_thickness=3, text_scale=1.5)

    def predict(self, frame):
        results = self.model.track(frame, stream=True)

        return results

    def plot_bboxes(self, results, frame):
        # cv2.line(frame, self.checkline[0], self.checkline[1], (46, 162, 112), 3)
        # xyxys = []
        # confidences = []
        # class_ids = []

        # for result in results:
        #    xyxys.append(result.boxes.xyxy.cpu().numpy())
        #    confidences.append(result.boxes.conf.cpu().numpy())
        #    class_ids.append(result.boxes.cls.cpu().numpy().astype(int))

        # Setup detections for visualization
        detections = sv.Detections(
            xyxy=results[0].boxes.xyxy.cpu().numpy(),
            confidence=results[0].boxes.conf.cpu().numpy(),
            class_id=results[0].boxes.cls.cpu().numpy().astype(int),
            tracker_id=results[0].boxes.id.cpu().numpy().astype(int)
        )

        # Format custom labels
        self.labels = [f"{self.CLASS_NAMES_DICT[class_id]} {confidence:0.2f}"
                       for _, confidence, class_id, tracker_id
                       in detections]

        self.nbTrucks = len(results.boxes.id)

        # Annotate and display frame
        frame = self.box_annotator.annotate(scene=frame, detections=detections, labels=self.labels)

        yield frame, self.nbTrucks

    def __call__(self):

        cap = cv2.VideoCapture(self.source)
        assert cap.isOpened()
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self.width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self.height)

        timer = 0

        while True:

            # start_time = time()

            ret, frame = cap.read()

            assert ret

            results = self.predict(frame)
            frame, nbTrucks = self.plot_bboxes(results, frame)

            # end_time = time()
            # fps = 1 / np.round(end_time - start_time, 2)

            # cv2.putText(frame, f'FPS: {int(fps)}', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 2)

            # cv2.imshow('Road Damage Detection', frame)

            response = DetectorResponse(frame=frame, nbTrucks=nbTrucks)

            yield response

            if cv2.waitKey(5) & 0xFF == 27:
                break

        cap.release()
        cv2.destroyAllWindows()
