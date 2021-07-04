# НЕКОРРЕКТО РАБОТАЕТ ОТРИСОВКА МАШИНЫ

import math

import pygame

from abstract_classes import GameObject, Observable
from sensor import Sensor


class Car(GameObject, Observable):
    WIDTH = 10  # Ширина автомобиля в см, 1см = 1px
    LENGTH = 20  # Длина автомобиля в см, 1см = 1px
    RADIUS = 15  # Радиус поворота автомобиля, см
    ACCELERATION = 0.001
    INIT_ORIENTATION = 0  # Градусы. Автомобиль перпендикулярен оси X
    MAX_SPEED = 0.3

    WHITE = (255, 255, 255)

    def __init__(self, x, y):
        super(Car, self).__init__()
        self._x = x
        self._y = y
        self._orientation = math.radians(Car.INIT_ORIENTATION)
        self.sensor = Sensor(self._x, self._y, self._orientation)
        self._attach(self.sensor)
        self._velocity = 0
        self._ang_velocity = 0  # Угловая скорость рад/с

    def _notify(self):
        for observer in self._observers:
            observer.update(self._x, self._y, self._orientation)

    def move(self, action: int) -> None:
        if action == 1:
            self.accelerate()
        elif action == 2:
            self._move_left()
        elif action == 3:
            self._move_right()
        self.rubbing_force()
        self._move_forward()
        self._notify()

    def _update_velocity(self, velocity: float) -> None:
        self._velocity = velocity
        self._ang_velocity = self._velocity / Car.RADIUS

    def accelerate(self) -> None:
        velocity = self._velocity + Car.ACCELERATION
        if velocity <= Car.MAX_SPEED:
            self._update_velocity(velocity)

    def brake(self) -> None:
        velocity = self._velocity - 2 * Car.ACCELERATION
        if velocity >= 0:
            self._update_velocity(velocity)

    def rubbing_force(self) -> None:
        velocity = self._velocity - 0.5 * Car.ACCELERATION
        if velocity >= 0:
            self._update_velocity(velocity)

    def _move_forward(self) -> None:
        # Автомобиль движется сверху вниз
        self._y += self._velocity * math.cos(self._orientation)
        self._x += self._velocity * math.sin(self._orientation)

    def _move_left(self) -> None:
        rotation_angle = self._calc_angle()
        self._orientation += rotation_angle

    def _move_right(self) -> None:
        rotation_angle = self._calc_angle()
        self._orientation -= rotation_angle

    def _calc_angle(self) -> float:
        # Длина хорды дуги при повороте автомобиля
        arc_angle = self._ang_velocity  # Угол дуги, описываемой при повороте
        rotation_angle = arc_angle / 2  # Угол отклонения автомобиля при повороте
        return rotation_angle

    def show(self, surface) -> None:  # Некорректно работает
        """
        При отрисовке сдвигает точка верхняя левая
        """
        raise NotImplementedError
