import math
from typing import Any

import pygame

from abstract_classes import GameObject, Observer, Observable
from ray import Ray


class Sensor(GameObject, Observer, Observable):
    DEFAULT_ANGLE_STEP_DEGREE = 4
    DEFAULT_ANGLE_STEP_RAD = math.radians(DEFAULT_ANGLE_STEP_DEGREE)
    AOV = 120  # Угол обзора сенсора, градусы
    MAX_RAY_LEN = 200  # Дальность луча, см

    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)
    YELLOW = (255, 255, 100)
    PURPLE = (150, 50, 150)

    def __init__(self, x: Any, y: Any, orientation: Any):
        super(Sensor, self).__init__()
        self._x = x
        self._y = y
        self._ray = Ray(self._x, self._y, Sensor.MAX_RAY_LEN)
        self._orientation = orientation  # Направление центра
        self._left_limit = math.radians(self._orientation + Sensor.AOV / 2)
        self._right_limit = math.radians(self._orientation - Sensor.AOV / 2)
        self._attach(self._ray)

    def _notify(self):
        for observer in self._observers:
            observer.update(self._x, self._y)

    def get_view(self, obstacles: Any) -> Any:  # Получить с сенсора данные об окружении
        view = []  # Карта мира
        angle = self._right_limit  # Начальный угол
        for _ in range(0, Sensor.AOV, Sensor.DEFAULT_ANGLE_STEP_DEGREE):
            ray_end_x = math.sin(angle) * Sensor.MAX_RAY_LEN  # Получить относительные
            ray_end_y = math.cos(angle) * Sensor.MAX_RAY_LEN  # координаты конца луча
            ray_end_x, ray_end_y = self._ray.translate(ray_end_x, ray_end_y)  # Перевести относительные коррдинаты
            # конца луча в абсолютные
            self._ray.look_at(ray_end_x, ray_end_y)  # Перенести конец луча в новую точку
            distance = self._get_distance(obstacles)  # Получить дистанцию до объекта
            view.append(distance)  # Записать данные
            angle += Sensor.DEFAULT_ANGLE_STEP_RAD
        return view

    def _get_distance(self, obstacles: Any) -> Any:  # Определить расстояние до точки пересечения
        closest = Sensor.MAX_RAY_LEN
        points = [self._ray.cast(*obstacle.get_coord()) for obstacle in obstacles]
        distances = [self._ray.get_distance(*point) for point in points if point]
        if distances:
            return min(distances)
        else:
            return closest

    def update(self, x: float, y: float, orientation: float) -> None:
        self._x = x
        self._y = y
        self._orientation = orientation
        self._upd_ray_limits()
        self._notify()

    def _upd_ray_limits(self) -> None:
        self._left_limit = self._orientation + math.radians(Sensor.AOV / 2)
        self._right_limit = self._orientation - math.radians(Sensor.AOV / 2)

    def show(self, surface):  # Отрисовка поля зрения сенсора
        x_r = math.sin(self._right_limit) * Sensor.MAX_RAY_LEN
        y_r = math.cos(self._right_limit) * Sensor.MAX_RAY_LEN

        coord_r = self._ray.translate(x_r, y_r)  # координаты конца правой грани

        x_l = math.sin(self._left_limit) * Sensor.MAX_RAY_LEN
        y_l = math.cos(self._left_limit) * Sensor.MAX_RAY_LEN

        coord_l = self._ray.translate(x_l, y_l)  # координаты конца правой грани

        x_c = math.sin(self._orientation) * Sensor.MAX_RAY_LEN
        y_c = math.cos(self._orientation) * Sensor.MAX_RAY_LEN

        coord_c = self._ray.translate(x_c, y_c)

        coord_30 = self._ray.translate(math.sin(self._orientation - math.radians(30)) * Sensor.MAX_RAY_LEN,
                                       math.cos(self._orientation - math.radians(30)) * Sensor.MAX_RAY_LEN)

        coord_90 = self._ray.translate(math.sin(self._orientation + math.radians(30)) * Sensor.MAX_RAY_LEN,
                                       math.cos(self._orientation + math.radians(30)) * Sensor.MAX_RAY_LEN)

        pygame.draw.line(surface,
                         Sensor.RED,
                         (self._x, self._y),
                         coord_r)

        pygame.draw.line(surface,
                         Sensor.GREEN,
                         (self._x, self._y),
                         coord_l)

        pygame.draw.line(surface,
                         Sensor.WHITE,
                         (self._x, self._y),
                         coord_c)

        pygame.draw.line(surface,
                         Sensor.YELLOW,
                         (self._x, self._y),
                         coord_30)

        pygame.draw.line(surface,
                         Sensor.PURPLE,
                         (self._x, self._y),
                         coord_90)

        pygame.draw.arc(surface,
                        (255, 0, 0),
                        pygame.Rect(self._x - Sensor.MAX_RAY_LEN,
                                    self._y - Sensor.MAX_RAY_LEN,
                                    Sensor.MAX_RAY_LEN * 2,
                                    Sensor.MAX_RAY_LEN * 2),
                        self._orientation - math.radians(Sensor.AOV / 2) - math.radians(90),
                        self._orientation + math.radians(Sensor.AOV / 2) - math.radians(90))
