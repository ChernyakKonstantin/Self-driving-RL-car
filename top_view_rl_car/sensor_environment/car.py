import math

import pygame.draw

from .abstract_classes import GameObject, Observable, Resetable
from .colors import Colors
from .sensor import Sensor


class Car(Observable, GameObject, Resetable):
    INIT_ORIENTATION = 0  # Градусы. Автомобиль перпендикулярен оси X

    MIN_STEERING_ANGLE = -45.0
    MAX_STEERING_ANGLE = 45.0
    MIN_SPEED = -2.0
    MAX_SPEED = 2.0
    SIZE = 10

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __init__(self, x, y):
        super().__init__()
        self._init_x = x
        self._init_y = y
        self._x = self._init_x
        self._y = self._init_y
        self._orientation = math.radians(Car.INIT_ORIENTATION)
        self._velocity = 0

        self.sensor = Sensor(self._x, self._y, self._orientation)
        self.attach(self.sensor)

    def _notify(self):
        for observer in self._observers:
            observer.update(self._x, self._y, self._orientation)

    def move(self, steering_angle: float, velocity: float) -> None:
        self._update_velocity(velocity)
        self._steer(steering_angle)
        self._update_coordinates()
        self._notify()

    def _update_velocity(self, velocity: float) -> None:
        self._velocity = velocity

    def _steer(self, cur_angle: float) -> None:
        self._orientation = math.radians(cur_angle)

    def _update_coordinates(self) -> None:
        # Автомобиль движется сверху вниз
        self._y += self._velocity * math.cos(self._orientation)
        self._x += self._velocity * math.sin(self._orientation)

    def reset(self):
        self._x = self._init_x
        self._y = self._init_y
        self._orientation = math.radians(Car.INIT_ORIENTATION)
        self._velocity = 0
        self._notify()

    def show(self, surface) -> None:
        pygame.draw.circle(surface, Colors.PURPLE, (self._x, self._y), Car.SIZE, 0)
        self.sensor.show(surface)

