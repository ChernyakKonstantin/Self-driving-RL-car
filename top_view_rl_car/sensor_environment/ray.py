import math
from typing import Any, Tuple, Union

from numba import jit

from .abstract_classes import GameObject, Observer


@jit
def get_intersection_compiled(x1: float, y1: float, x2: float, y2: float,
                              x3: float, y3: float, x4: float, y4: float) -> Union[Tuple[float, float], None]:
    """
    Если луч пересекает объект, возвращает координаты точки пересечения,
    в противном случае None
    """
    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None
    x_nom = (x1 * y1 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)
    y_nom = (x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)
    x = x_nom / denom
    y = y_nom / denom
    on_line_1 = (x1 <= x <= x2 or x1 >= x >= x2) and (y1 <= y <= y2 or y1 >= y >= y2)
    on_line_2 = (x3 <= x <= x4 or x3 >= x >= x4) and (y3 <= y <= y4 or y3 >= y >= y4)
    if on_line_1 and on_line_2:
        return x, y
    else:
        return None


class Ray(GameObject, Observer):
    def __init__(self, x: Any, y: Any, max_ray_len: Any):
        self._x = x
        self._y = y
        self.max_ray_len = max_ray_len
        # Координаты конечной точки луча
        self._end_x = None
        self._end_y = None

    def translate(self, x: float, y: float) -> Tuple[float, float]:
        # Переводит относительные от источника луча координаты в абсолютные
        new_x = self._x + x
        new_y = self._y + y
        return new_x, new_y

    def cast(self, x1: float, y1: float, x2: float, y2: float) -> Union[Tuple[float, float], None]:
        return get_intersection_compiled(self._x, self._y, self._end_x, self._end_y, x1, y1, x2, y2)

    def look_at(self, x: Any, y: Any) -> None:
        self._end_x = x
        self._end_y = y

    def update(self, x: Any, y: Any) -> None:
        self._x = x
        self._y = y

    def get_distance(self, intersection_x: Any, intersection_y: Any) -> Any:
        x = intersection_x - self._x
        y = intersection_y - self._y
        return math.sqrt(pow(x, 2) + pow(y, 2))

    def show(self, surface: Any) -> None:
        raise NotImplementedError
