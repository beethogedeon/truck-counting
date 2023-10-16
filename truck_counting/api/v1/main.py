from os.path import join

from truck_counting.models import TruckDetector, DetectorResponse

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse

from pydantic import BaseModel
import numpy as np
from PIL import Image

api = FastAPI(title="Truck Counting")


class DetectRequest(Request):
    source: str | int | np.ndarray | Image.Image = 0


@api.get("/", include_in_schema=False, tags=["General"])
def index(request: Request):
    return RedirectResponse(join(request.url.path, "docs"))


@api.get("/detect", tags=["General"], response_model=DetectorResponse)
def run(request: DetectRequest):
    truck_detector = TruckDetector(request.source)
    truck_detector()

