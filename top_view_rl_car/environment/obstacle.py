from typing import Any, Tuple

import pygame

from .abstract_classes import GameObject


class Line(GameObject):
    WHITE = (255, 255, 255)
    """ Класс линий, из которых состоит препятствие."""

    def __init__(self, x1, y1, x2, y2):
        self._start_point = pygame.Vector2(x1, y1)
        self._end_point = pygame.Vector2(x2, y2)

    def shifted_copy(self, shift: Any) -> Any:
        a = self._start_point.x + shift, self._start_point.y
        b = self._end_point.x + shift, self._end_point.y
        return Line(*a, *b)

    def show(self, surface):
        pygame.draw.line(surface,
                         Line.WHITE,
                         (self._start_point.x, self._start_point.y),
                         (self._end_point.x, self._end_point.y))

    def get_coord(self) -> Tuple:
        return self._start_point.x, self._start_point.y, self._end_point.x, self._end_point.y
