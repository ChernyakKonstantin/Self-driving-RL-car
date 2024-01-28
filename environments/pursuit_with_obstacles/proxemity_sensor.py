import cv2
import numpy as np

from .detectable import Detectable
from .spatial import Spatial


class ProxemitySensor(Spatial):
    "X is right, Y is Down. This is image coordinates."

    # Length is X.
    def __init__(
        self,
        position: np.ndarray = np.array([0.0, 0.0]),
        orientation: float = 0.0,
        max_distance: float = 20.0,
        segments: int = 100,
    ):
        self.max_distance = max_distance
        self.distances = np.linspace(0, max_distance, segments)
        self.points = np.stack([np.linspace(0, max_distance, segments), np.zeros(segments)], axis=1)
        super().__init__(position, orientation)

    def get_distance(self, object: Detectable) -> float:
        # Go from closest to farthest
        for i, point in enumerate(self.points):
            if object.contains(point):
                return self.distances[i]
        return self.max_distance

    def render(self, image: np.ndarray) -> None:
        cast = lambda x: np.round(x).astype(int)
        cv2.line(image, cast(self.points[0]), cast(self.points[-1]), (255, 0, 255), 1)
