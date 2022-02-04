# Проверить все линии для правой границы сенсора. Если нет пересечений - исключить все правые стенки
# Если пересечения есть - найти минимальную по Y точку пересечения. Исключить правые стенки с Y < найденный Y. Исключить стенки с Y > найденный Y + MAX_RAY_LEN
# Проверить все линии для левой границы сенсора. Если нет пересечений - исключить все левые стенки
# Если пересечения есть - найти минимальную по Y точку пересечения. Исключить левые стенки с Y < найденный Y. Исключить стенки с Y > найденный Y + MAX_RAY_LEN

import math
from typing import Any

import pygame

from .abstract_classes import GameObject, Observer, Observable
from .colors import Colors
from .ray import Ray


class Sensor(GameObject, Observer, Observable):
    _DEFAULT_ANGLE_STEP_DEGREE = 4
    _DEFAULT_ANGLE_STEP_RAD = math.radians(_DEFAULT_ANGLE_STEP_DEGREE)
    _AOV = 120  # Угол обзора сенсора, градусы
    _MAX_RAY_LEN = 200  # Дальность луча, см

    @classmethod
    def get_max_ray_len(cls):
        return cls._MAX_RAY_LEN

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
        self.attach(self._ray)

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

    def _get_ray_y_min_max(self):
        end_points = []
        for angle in range(0, Sensor._AOV, Sensor._DEFAULT_ANGLE_STEP_DEGREE):
            end_points.append(math.cos(self._right_limit + math.radians(angle)) * Sensor._MAX_RAY_LEN)
        return min(end_points), max(end_points)

    def filter_obstacles(self, obstacles: list) -> list:
        """Метод фильтрации препятствий, которые не попадут в поле видимости."""
        ray_end_y_min, ray_end_y_max = self._get_ray_y_min_max()
        ray_y_min = min([ray_end_y_min, self._ray._y])
        ray_y_max = max([ray_end_y_max, self._ray._y])
        # Множество линий, для которых конец < y _min
        obstacles_above_vision_field = set(obs for obs in obstacles if obs._end_point.y < ray_y_min)
        # Множество линий, для которых начало > y_max
        obstacles_below_vision_field = set(obs for obs in obstacles if obs._start_point.y > ray_y_max)
        return list(set(obstacles) - obstacles_above_vision_field - obstacles_below_vision_field)

    def get_view(self, obstacles: list) -> list:  # Получить с сенсора данные об окружении
        view = []  # Карта мира
        for angle in range(0, Sensor._AOV, Sensor._DEFAULT_ANGLE_STEP_DEGREE):
            # Получить относительные координаты конца луча
            ray_end_x = math.sin(self._right_limit + math.radians(angle)) * Sensor._MAX_RAY_LEN
            ray_end_y = math.cos(self._right_limit + math.radians(angle)) * Sensor._MAX_RAY_LEN
            # Получить абсолютные координаты конца луча
            ray_end_x, ray_end_y = self._ray.translate(ray_end_x, ray_end_y)
            # Перенести конец луча в новую точку
            self._ray.look_at(ray_end_x, ray_end_y)
            # Получить дистанцию до объекта
            distance = self._get_distance(obstacles)
            view.append(distance)
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
