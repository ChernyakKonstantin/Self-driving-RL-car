from typing import Union, Tuple

import pygame.draw

from .abstract import GameObject, Observable, Resetable
from .sensor import Sensor


class Car(Observable, GameObject, Resetable):
    """
    The car have a sensor to obtain observations.
    The car is driven forward automatically. The only control is steering.
    The car keeps the last steering value and accepts change of the value.
    """

    def __init__(self,
                 x: Union[float, int],
                 y: Union[float, int],
                 orientation: float,
                 velocity: float = 2.0,
                 steering_bounds: Tuple[float, float] = (-45.0, 45.0),
                 sprite_size: float = 10,
                 n_rays: int = 30,
                 angle_of_view: int = 120,
                 ray_length: float = 200):
        super().__init__()
        self._position = pygame.Vector2(x, y)
        self._orientation = orientation
        self._velocity = velocity
        self._steering_bounds = {"min": steering_bounds[0], "max": steering_bounds[1]}
        self._sprite_size = sprite_size
        self.sensor = Sensor(self._position.x,
                             self._position.y,
                             self._orientation,
                             n_rays,
                             angle_of_view,
                             ray_length)
        self.attach(self.sensor)

    def _notify(self):
        for observer in self._observers:
            observer.update(self._position.x,
                            self._position.y,
                            self._orientation)

    def move(self, steering_delta: float) -> None:
        """
        The method updates position of the car and its observers.
        Args:
            steering_delta: Delta of steering.
        """
        self._steer(steering_delta)
        self._notify()

    def _steer(self, steering_delta: float) -> None:
        """
        The method updates the car orientation with checking of bounds.
        Args:
            steering_delta: Delta of steering.
        """
        orientation = self._orientation + steering_delta
        if orientation > self._steering_bounds["max"]:
            self._orientation = self._steering_bounds["max"]
        elif orientation < self._steering_bounds["min"]:
            self._orientation = self._steering_bounds["min"]
        else:
            self._orientation = orientation

    def reset(self,
              x: Union[float, int],
              y: Union[float, int],
              orientation: float):
        self._position = pygame.Vector2(x, y)
        self._orientation = orientation
        self._notify()

    def show(self, surface) -> None:
        self.sensor.show(surface)
        pygame.draw.circle(surface,
                           pygame.Color('purple'),
                           (self._position.x, self._position.y),
                           self._sprite_size,
                           width=0)
