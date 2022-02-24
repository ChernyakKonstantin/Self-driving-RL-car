from typing import Tuple, Any

import numpy as np
import pygame

from .abstract import GameObject


class SensorViewer(GameObject):
    """
    Simple visualization of world representation by sensor.
    """

    def __init__(self, position: pygame.Vector2, n_distances: int, size: Tuple = (100, 50), max_distance: float = 50):
        """
        Args:
            position: Location of the viewer (x,y).
            n_distances: Number of a sensor rays.
            size: Width and height of the viewer.
            max_distance: The maximal distance value.
        """
        self._position = position
        self._n_distances = n_distances
        self._size = size
        self._max_distance = max_distance
        self._x_coordinates = self._compute_line_x_coordinates()
        self._y_high = position.y
        self._y_low = position.y + size[1]
        self._distances = None

    def _compute_line_x_coordinates(self) -> np.ndarray:
        """
        The method computes position of the viewer lines on the X-axis
        Returns: Computed position of the viewer lines on the X-axis.
        """
        return np.linspace(0, self._size[0], self._n_distances) + self._position.x

    def update(self, distances: np.ndarray) -> None:
        """
        The method sets data of the intersection points distances from the sensor.
        Args:
            distances: Intersection points distances from the sensor.
        """
        self._distances = distances

    def _compute_intensity(self) -> np.ndarray:
        """
        The method computes intensity value for each element of distances data.
        Returns: Intensity for each element of data.
        """
        return ((1 - self._distances / self._max_distance) * 255).astype(int)

    def show(self, surface: Any) -> None:
        pygame.draw.rect(surface,
                         color=pygame.Color("black"),
                         rect=(*self._position, *self._size))
        intensities = self._compute_intensity()
        for x, value in zip(self._x_coordinates, intensities):
            pygame.draw.line(surface,
                             [value] * 3,
                             (x, self._y_high),
                             (x, self._y_low))
        pygame.draw.rect(surface,
                         color=pygame.Color("white"),
                         rect=(*self._position, *self._size),
                         width=1)
