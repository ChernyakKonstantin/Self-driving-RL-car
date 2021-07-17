import math
from typing import Any
from colors import Colors

import pygame

from abstract_classes import GameObject, Observer, Observable
from ray import Ray


class Sensor(GameObject, Observer, Observable):
    _DEFAULT_ANGLE_STEP_DEGREE = 4
    _DEFAULT_ANGLE_STEP_RAD = math.radians(_DEFAULT_ANGLE_STEP_DEGREE)
    _AOV = 120  # Угол обзора сенсора, градусы
    _MAX_RAY_LEN = 200  # Дальность луча, см

    @classmethod
    def get_observation_shape(cls):
        return int(cls._AOV / cls._DEFAULT_ANGLE_STEP_DEGREE)

    def __init__(self, x: Any, y: Any, orientation: Any):
        super(Sensor, self).__init__()
        self._x = x
        self._y = y
        self._ray = Ray(self._x, self._y, Sensor._MAX_RAY_LEN)
        self._orientation = orientation  # Направление центра
        self._left_limit = math.radians(self._orientation + Sensor._AOV / 2)
        self._right_limit = math.radians(self._orientation - Sensor._AOV / 2)
        self._attach(self._ray)

    def _notify(self) -> None:
        for observer in self._observers:
            observer.update(self._x, self._y)

    def _get_distance(self, obstacles: list) -> float:
        """
        Функция определения расстояния до точки пересечения.
        Если точка пересечения отсутствует, вернуть максимальную длину луча.
        """
        points = [self._ray.cast(*obstacle.get_coord()) for obstacle in obstacles]
        distances = [self._ray.get_distance(*point) for point in points if point]
        if distances:
            return min(distances)
        else:
            return Sensor._MAX_RAY_LEN

    def get_view(self, obstacles: list) -> list:  # Получить с сенсора данные об окружении
        view = []  # Карта мира
        angle = self._right_limit  # Начальный угол
        for _ in range(0, Sensor._AOV, Sensor._DEFAULT_ANGLE_STEP_DEGREE):
            # Получить относительные координаты конца луча
            ray_end_x = math.sin(angle) * Sensor._MAX_RAY_LEN
            ray_end_y = math.cos(angle) * Sensor._MAX_RAY_LEN
            # Получить абсолютные координаты конца луча
            ray_end_x, ray_end_y = self._ray.translate(ray_end_x, ray_end_y)
            # Перенести конец луча в новую точку
            self._ray.look_at(ray_end_x, ray_end_y)
            # Получить дистанцию до объекта
            distance = self._get_distance(obstacles)
            view.append(distance)
            angle += Sensor._DEFAULT_ANGLE_STEP_RAD
        return view

    def _upd_ray_limits(self) -> None:
        self._left_limit = self._orientation + math.radians(Sensor._AOV / 2)
        self._right_limit = self._orientation - math.radians(Sensor._AOV / 2)

    def update(self, x: float, y: float, orientation: float) -> None:
        self._x = x
        self._y = y
        self._orientation = orientation
        self._upd_ray_limits()
        self._notify()

    def show(self, surface) -> None:  # Отрисовка поля зрения сенсора

        coord_r = self._ray.translate(math.sin(self._right_limit) * Sensor._MAX_RAY_LEN,
                                      math.cos(self._right_limit) * Sensor._MAX_RAY_LEN)

        coord_l = self._ray.translate(math.sin(self._left_limit) * Sensor._MAX_RAY_LEN,
                                      math.cos(self._left_limit) * Sensor._MAX_RAY_LEN)

        coord_c = self._ray.translate(math.sin(self._orientation) * Sensor._MAX_RAY_LEN,
                                      math.cos(self._orientation) * Sensor._MAX_RAY_LEN)

        coord_c_r = self._ray.translate(math.sin(self._orientation - math.radians(30)) * Sensor._MAX_RAY_LEN,
                                        math.cos(self._orientation - math.radians(30)) * Sensor._MAX_RAY_LEN)

        coord_c_l = self._ray.translate(math.sin(self._orientation + math.radians(30)) * Sensor._MAX_RAY_LEN,
                                        math.cos(self._orientation + math.radians(30)) * Sensor._MAX_RAY_LEN)

        pygame.draw.line(surface,
                         Colors.RED,
                         (self._x, self._y),
                         coord_r)

        pygame.draw.line(surface,
                         Colors.GREEN,
                         (self._x, self._y),
                         coord_l)

        pygame.draw.line(surface,
                         Colors.WHITE,
                         (self._x, self._y),
                         coord_c)

        pygame.draw.line(surface,
                         Colors.YELLOW,
                         (self._x, self._y),
                         coord_c_r)

        pygame.draw.line(surface,
                         Colors.PURPLE,
                         (self._x, self._y),
                         coord_c_l)

        pygame.draw.arc(surface,
                        (255, 0, 0),
                        pygame.Rect(self._x - Sensor._MAX_RAY_LEN,
                                    self._y - Sensor._MAX_RAY_LEN,
                                    Sensor._MAX_RAY_LEN * 2,
                                    Sensor._MAX_RAY_LEN * 2),
                        self._orientation - math.radians(Sensor._AOV / 2) - math.radians(90),
                        self._orientation + math.radians(Sensor._AOV / 2) - math.radians(90))
