import cv2
import numpy as np

from .spatial import Spatial


class Detectable(Spatial):
    # Rectangle.
    # Center is rear center to enable the class reuse for NPC cars.
    # Width is Y, length is X.
    def __init__(
        self, position: np.ndarray = np.array([0., 0.]), orientation: float = 0.0, width: float = 3., length: float = 4.
    ):
        self.width = width
        self.length = length
        self.points = np.asarray(
            [
                [0, -width / 2],
                [length, -width / 2],
                [length, width / 2],
                [0, width / 2],
            ]
        )
        self.area = width * length
        super().__init__(position, orientation)

    @staticmethod
    def _calc_triangle_area(p1: np.ndarray, p2: np.ndarray, p3: np.ndarray) -> float:
        x1, y1 = p1
        x2, y2 = p2
        x3, y3 = p3
        return 0.5 * abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1))

    def contains(self, point: np.ndarray) -> bool:
        area1 = self._calc_triangle_area(point, self.points[0], self.points[1])
        area2 = self._calc_triangle_area(point, self.points[1], self.points[2])
        area3 = self._calc_triangle_area(point, self.points[2], self.points[3])
        area4 = self._calc_triangle_area(point, self.points[3], self.points[0])
        area_sum = area1 + area2 + area3 + area4
        return abs(area_sum - self.area) < 1e-3

    def render(self, image: np.ndarray) -> None:
        cast = lambda x: np.round(x).astype(int)
        cv2.line(image, cast(self.points[0]), cast(self.points[1]), (0, 0, 0), 1)
        cv2.line(image, cast(self.points[1]), cast(self.points[2]), (0, 0, 0), 1)
        cv2.line(image, cast(self.points[2]), cast(self.points[3]), (0, 0, 0), 1)
        cv2.line(image, cast(self.points[3]), cast(self.points[0]), (0, 0, 0), 1)
