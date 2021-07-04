import math
from typing import Any, Union

from abstract_classes import GameObject, Observer


class Ray(GameObject, Observer):  # Класс луча
    WHITE = (255, 255, 255)

    def __init__(self, x: Any, y: Any, max_ray_len: Any) -> None:
        self._x = x
        self._y = y
        self.max_ray_len = max_ray_len
        # Координаты конечной точки луча
        self._x_end = None
        self._y_end = None
        # Координаты точки пересечения с препятствием
        self._intersection_x = None
        self._intersection_y = None

    def translate(self, x: Any, y: Any) -> Any:
        # Переводит относительные от источника луча координаты в абсолютные
        new_x = self._x + x
        new_y = self._y + y
        return new_x, new_y

    def cast(self, x1: Any, y1: Any, x2: Any, y2: Any) -> Union[Any, None]:
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
                self._intersection_x = x
                self._intersection_y = y
                return x, y
            else:
                return None
        else:
            self._intersection_x = None
            self._intersection_y = None
            return None

    def look_at(self, x: Any, y: Any) -> None:
        self._x_end = x
        self._y_end = y

    def update(self, x: Any, y: Any) -> None:
        self._x = x
        self._y = y

    def get_distance(self, _intersection_x: Any, _intersection_y: Any) -> Any:
        x = _intersection_x - self._x
        y = _intersection_y - self._y
        return math.sqrt(pow(x, 2) + pow(y, 2))

    def show(self, surface: Any) -> None:
        raise NotImplementedError
