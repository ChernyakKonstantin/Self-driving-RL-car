import math
from typing import Tuple, Union

import pygame

from .abstract import GameObject
from .point import Point


class Line(GameObject):
    WHITE = (255, 255, 255)
    """
    Line is a basic object that forms a road part.
    """

    def __init__(self, start_point: Point, end_point: Point):
        self._start_point = start_point
        self._end_point = end_point

    def show(self, surface):
        pygame.draw.line(surface,
                         Line.WHITE,
                         self._start_point.position,
                         self._end_point.position)

    def get_coord(self) -> Tuple[Union[float, int]]:
        return *self._start_point.position, *self._end_point.position

    def extrude(self, shift: float) -> Tuple:
        """
        The method return right and left points
        """
        lines = []
        for delta_angle in (-90, 90):
            points = []
            for point in ([self._start_point, self._end_point]):
                x = (point.position.x
                     + math.sin(math.radians(point.orientation + delta_angle)) * shift)
                y = (point.position.y
                     + math.cos(math.radians(point.orientation + delta_angle)) * shift)
                points.append(Point(x, y, point.orientation))
            lines.append(Line(*points))
        return lines
