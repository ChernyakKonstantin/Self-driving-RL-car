from typing import Union

import numpy as np


class CollisionDetector:
    def __init__(self, collision_radius: Union[float, int]):
        self._collision_radius = collision_radius

    def check(self, distances: np.ndarray) -> bool:
        return np.any(distances <= self._collision_radius)
