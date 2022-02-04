import random
from typing import Tuple

from .abstract import GameObject, Resetable
from .obstacle import Line
import numpy as np

class World(GameObject, Resetable):
    _WALL_X_SHIFT = 25
    _WALL_Y_SHIFT = 25
    _ROAD_WIDTH = 100

    @property
    def walls(self):
        return self._walls

    def __init__(self, x_start: float, y_start: float, length: float):
        self._x_start = x_start
        self._y_start = y_start
        self._x_end = self._x_start + length
        self._walls = []

    def reset(self) -> None:
        self._walls = []
        self.generate()

    def generate(self) -> None:
        x1, y1 = self._x_start, self._y_start
        x2, y2 = self._x_start, self._y_start
        while x1 < self._x_end:
            x2 = x1 + random.choice([-1, 1]) * random.randint(0, World._WALL_X_SHIFT)
            y2 = y1 + random.randint(0, World._WALL_Y_SHIFT)
            self.walls.append(Line(x1, y1, x2, y2))
            x1, y1 = x2, y2
        walls_count = len(self.walls)
        # for index in range(walls_count):
        #     self.walls.append(self.walls[index].shifted_copy(World._ROAD_WIDTH))

        # Верхняя граница
        self.walls.append(Line(self._x_start, self._y_start,
                               self._x_start + World._ROAD_WIDTH, self._y_start))

        # Нижняя граница
        self.walls.append(Line(x2, y2,
                               x2 + World._ROAD_WIDTH, y2))


    def to_points_array(self) -> Tuple[np.ndarray]:
        # return np.reshape([wall.get_coord() for wall in self._walls], (len(self._walls), 2, 2))
        data = np.array([wall.get_coord() for wall in self._walls])
        x1 = data[:, 0]
        y1 = data[:, 1]
        x2 = data[:, 2]
        y2 = data[:, 3]
        return x1, y1, x2, y2

    def show(self, surface):
        for wall in self._walls:
            wall.show(surface)
