import math
from typing import Any, Union, Tuple

from .abstract_classes import GameObject, Observer


class Ray(GameObject, Observer):  # Класс луча
    def __init__(self, x: Any, y: Any, max_ray_len: Any):
        self._x = x
        self._y = y
        self.max_ray_len = max_ray_len
        # Координаты конечной точки луча
        self._x_end = None
        self._y_end = None

    def translate(self, x: float, y: float) -> Tuple[float, float]:
        # Переводит относительные от источника луча координаты в абсолютные
        new_x = self._x + x
        new_y = self._y + y
        return new_x, new_y

    def cast(self, x1: float, y1: float, x2: float, y2: float) -> Union[Tuple[float, float], None]:
        """
        Если луч пересекает объект, возвращает координаты точки пересечения,
        в противном случае None
        """
        den = (x1 - x2) * (self._y - self._y_end) - (y1 - y2) * (self._x - self._x_end)
        if den == 0:
            return None

        t = ((x1 - self._x) * (self._y - self._y_end) - (y1 - self._y) * (self._x - self._x_end)) / den

        if 0 < t < 1:
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            x = int(x)
            y = int(y)
            # Проверка, что точка пересечения находится по направлению взгяда
            if self._x > x > self._x_end or self._x < x < self._x_end:
                return x, y
            else:
                return None
        else:
            return None

    def look_at(self, x: Any, y: Any) -> None:
        self._x_end = x
        self._y_end = y

    def update(self, x: Any, y: Any) -> None:
        self._x = x
        self._y = y

    def get_distance(self, intersection_x: Any, intersection_y: Any) -> Any:
        x = intersection_x - self._x
        y = intersection_y - self._y
        return math.sqrt(pow(x, 2) + pow(y, 2))

    def show(self, surface: Any) -> None:
        raise NotImplementedError
