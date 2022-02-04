from typing import Union

import numpy as np
import pygame

from .abstract import GameObject, Observer, Resetable
from .colors import Colors


class ColisionDetector(Observer, Resetable, GameObject):
    def __init__(self, object_center: Union[tuple, list], objects_radius: float,
                 min_distance_to_obstacle: float):
        # self._p1_coords = None
        # self._p2_coords = None
        # self._object_center = np.array([object_center, ])
        self._x0, self._y0 = object_center
        self._collision_zone_radius = objects_radius + min_distance_to_obstacle

    def update(self, x: float, y: float, *args, **kwargs) -> None:
        self._object_center = np.array([x, y])

    def check(self) -> bool:
        distances_to_walls = self.find_dist()
        distances_to_walls = np.nan_to_num(distances_to_walls, nan=np.inf)
        print(distances_to_walls.min())
        return np.any(distances_to_walls <= self._collision_zone_radius)

    def reset(self, x1, y1, x2, y2):
        self._x1 = x1
        self._y1 = y1
        self._x2 = x2
        self._y2 = y2

    # def reset(self, points: np.ndarray):
    #     """Points should have shape:
    #     [
    #      [[p11_x, p11_y], [p12_x, p12_y]],
    #      ...,
    #      [[pn1_x, pn1_y], [pn2_x, pn2_y]]
    #     ]
    #     """
    #     self._p1_coords = points[:, 0]
    #     self._p2_coords = points[:, 1]

    def show(self, surface):
        pygame.draw.circle(surface, Colors.GREEN, tuple(self._object_center), self._collision_zone_radius, 1)

    # def find_dist(self) -> np.ndarray:
    #     # """p1 - x and y of one line point, p2 - for another
    #     # Points should be like:
    #     # [[x1, y1],
    #     # [x2, y2]]
    #     # """
    #     denominator = np.sqrt(np.sum(np.square(self._p2_coords - self._p1_coords), axis=-1)).reshape(-1, 1)
    #     diff_1 = -1 * np.diff(np.flip((self._p2_coords - self._p1_coords), axis=-1) * self._object_center)
    #     diff_2 = -1 * np.diff(self._p2_coords * np.flip(self._p1_coords, axis=-1))
    #     numerator = np.abs(diff_1 + diff_2)
    #     return numerator / denominator


    def find_dist(self) -> np.ndarray:
        numerator = np.abs((self._y2 - self._y1) * self._x0 - (self._x2 - self._x1) * self._y0 + self._x2 * self._y1 - self._y2 * self._x1) 
        denominator = np.sqrt(np.square(self._y2 - self._y1) + np.square(self._x2 - self._x1))
        return numerator / denominator