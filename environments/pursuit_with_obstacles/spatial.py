import math

import numpy as np


def rot2d(angle: float, points: np.ndarray) -> np.ndarray:
    "Points should be of shape [N, 2]"
    matrix = np.asarray([[math.cos(angle), -math.sin(angle)], [math.sin(angle), math.cos(angle)]])
    return (matrix @ points.T).T


class Spatial:
    "X is right, Y is Down. This is image coordinates."

    def __init__(
        self,
        position: np.ndarray = np.array([0.0, 0.0]),
        orientation: float = 0.0,
    ):
        self.points: np.ndarray  # Shape is [N, 2]
        self.position = np.array([0.0, 0.0])
        self.orientation = 0.0
        self.update(position, orientation)

    def update(self, delta_pos: np.ndarray, delta_orient: float) -> None:
        self.points = rot2d(delta_orient, self.points)
        self.points = self.points + delta_pos
        self.position += delta_pos
        self.orientation += delta_orient
        if self.orientation > math.pi:
            self.orientation -= 2 * math.pi
        elif self.orientation < -math.pi:
            self.orientation += 2 * math.pi
