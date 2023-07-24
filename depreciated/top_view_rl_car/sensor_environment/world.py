import math
import random
from itertools import chain
from typing import Union

import numpy as np
import pygame

from .abstract import GameObject, Resetable
from .line import Line
from .point import Point


class World(GameObject, Resetable):

    def __init__(self,
                 world_width: Union[float, int],
                 world_length: Union[float, int],
                 n_points: int,
                 velocity: Union[float, int],
                 part_length: Union[float, int],
                 road_width: Union[float, int]):
        self._world_width = world_width
        self._world_length = world_length
        self._n_points = n_points
        self._velocity = velocity
        self._part_length = part_length
        self._road_width = road_width
        self.obstacle_coordinates = np.empty(shape=(4, n_points * 2), dtype=float)

    def _rotate(self, alpha, origin) -> None:
        """
        The method calculates shifts of the rays endpoints from the rays source.

        Returns: Deltas of x and deltas of y.
        """
        if not isinstance(origin, np.ndarray):
            origin = np.array(origin)
        if not origin.shape == (2, 1):
            origin = origin.reshape(2, 1)
        alpha = np.radians(alpha)
        rotation_matrix = np.array([[np.cos(alpha), -np.sin(alpha)],
                                    [np.sin(alpha), np.cos(alpha)]])
        relative_vec = self.obstacle_coordinates[[0, 2, 1, 3]].reshape(2, -1) - origin
        rotated = rotation_matrix @ relative_vec
        self.obstacle_coordinates = (rotated + origin).reshape(4, -1)[[0, 2, 1, 3]]

    def translate(self, alpha: Union[int, float], origin):
        """
        The method rotates and moves points to make an illusion of moving.
        Args:
            alpha: Rotation angle in degrees.
        """
        self._rotate(alpha, origin)
        self.obstacle_coordinates[[1, 3]] -= self._velocity

    def reset(self) -> None:
        self.generate()

    def generate(self):
        # A road part length in pixels
        delta_angle = [0, ]
        delta_angle.extend([random.randint(-45, 45) for _ in range(self._n_points - 2)])

        x = self._world_width / 2
        y = self._world_length / 2

        upper_point = Point(x, 0, orientation=0)
        initial_point = Point(x, y, orientation=0)
        points = [upper_point, initial_point, ]
        for i in range(1, len(delta_angle)):
            orientation = delta_angle[i - 1]
            d_x = math.sin(math.radians(orientation)) * self._part_length
            d_y = math.cos(math.radians(orientation)) * self._part_length
            x += d_x
            y += d_y
            points.append(Point(x, y, orientation))

        lines = chain.from_iterable([Line(points[i], points[i + 1]).extrude(20) for i in range(len(points) - 1)])
        for i, line in enumerate(lines):
            self.obstacle_coordinates[:, i] = (*line._start_point.position, *line._end_point.position)

    def show(self, surface):
        for i in range(self.obstacle_coordinates.shape[-1]):
            pygame.draw.line(surface,
                             pygame.Color("white"),
                             *self.obstacle_coordinates[:, i].reshape(2, 2),
                             width=1)

            # for i in range(self.obstacle_coordinates[[0,2,1,3]].reshape(2,-1).shape[-1]):
            #     pygame.draw.circle(surface,
            #                        pygame.Color("white"),
            #                        self.obstacle_coordinates[[0,2,1,3]].reshape(2,-1)[:, i],
            #                        radius=3)
