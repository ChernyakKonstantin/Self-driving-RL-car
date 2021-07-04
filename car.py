# НЕКОРРЕКТО РАБОТАЕТ ОТРИСОВКА МАШИНЫ

import math

import pygame

from abstract_classes import GameObject, Observable
from sensor import Sensor


class Car(GameObject, Observable):
    WIDTH = 10  # Ширина автомобиля в см, 1см = 1px
    LENGTH = 20  # Длина автомобиля в см, 1см = 1px
    RADIUS = 15  # Радиус поворота автомобиля, см
    VELOCITY = 1  # Скорость автомобиля см/с
    INIT_ORIENTATION = 0  # Градусы. Автомобиль перпендикулярен оси X
    ANG_VELOCITY = VELOCITY / RADIUS  # Угловая скорость рад/с

    WHITE = (255, 255, 255)

    def __init__(self, x, y):
        super(Car, self).__init__()
        self._x = x
        self._y = y
        self._orientation = math.radians(Car.INIT_ORIENTATION)
        self.sensor = Sensor(self._x, self._y, self._orientation)
        self._attach(self.sensor)

    def _notify(self):
        for observer in self._observers:
            observer.update(self._x, self._y, self._orientation)

    def move_forward(self):
        # Автомобиль движется сверху вниз
        self._y += Car.VELOCITY * math.cos(self._orientation)
        self._x += Car.VELOCITY * math.sin(self._orientation)
        self._notify()

    def move_left(self):
        rotation_angle = self.calc_angle()
        self._orientation += rotation_angle
        # self._notify()
        self.move_forward()

    def move_right(self):
        rotation_angle = self.calc_angle()
        self._orientation -= rotation_angle
        # self._notify()
        self.move_forward()

    def calc_angle(self):  # Длина хорды дуги при повороте автомобиля
        arc_angle = Car.ANG_VELOCITY  # Угол дуги, описываемой при повороте
        rotation_angle = arc_angle / 2  # Угол отклонения автомобиля при повороте
        return rotation_angle

    def show(self, surface):  # Некорректно работает
        """
        При отрисовке сдвигает точка верхняя левая
        """
        raise NotImplementedError
