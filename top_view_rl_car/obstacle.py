from typing import Any, Tuple

import pygame

from .abstract_classes import GameObject


class Point:
    @property
    def x(self) -> Any:
        return self._x

    @x.setter
    def x(self, value: Any) -> None:
        self._x = value

    @property
    def y(self) -> Any:
        return self._y

    @y.setter
    def y(self, value: Any) -> None:
        self._y = value

    def __init__(self, x: any, y: Any) -> None:
        self._x = x
        self._y = y


class Line(GameObject):
    WHITE = (255, 255, 255)
    """ Класс линий, из которых состоит препятствие."""

    def __init__(self, x1, y1, x2, y2):
        self._start_point = Point(x1, y1)
        self._end_point = Point(x2, y2)

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


class Obstacle(GameObject):
    def __init__(self, x: Any, y: Any, width: Any, height: Any):
        self._x = x
        self._y = y
        self._width = width
        self._height = height
        self._edges = []
        self._make_object()

    def _make_object(self):  # Создает прямоугольный объект
        self._edges.append(Line(self._x,
                                self._y,
                                self._x + self._width,
                                self._y))
        self._edges.append(Line(self._x + self._width,
                                self._y,
                                self._x + self._width,
                                self._y + self._height))
        self._edges.append(Line(self._x,
                                self._y + self._height,
                                self._x + self._width,
                                self._y + self._height))
        self._edges.append(Line(self._x,
                                self._y,
                                self._x,
                                self._y + self._height))

    def show(self, surface):
        for edge in self._edges:
            edge.show(surface)
