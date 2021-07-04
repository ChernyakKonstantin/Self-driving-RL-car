import pygame
import math
from abstract_classes import GameObject, Observable
from typing import Any


class RadarView(GameObject):
    RED = (255, 0, 0)
    GREEN = (0, 255, 0)
    WHITE = (255, 255, 255)

    def __init__(self):
        self._x = 400
        self._y = 400
        self._diameter = 200
        self._radius = 1
        self._forbidden_radius = 5  # Пока здесь вручную ввожу

    def show(self, surface: Any, view: Any) -> None:  # Отрисовка карты
        for dot in enumerate(view):
            if dot[1]:
                angle = math.radians(4 * dot[0] + 120)
                distance = self._diameter / 2 * (dot[1] / 200)

                start_point = (int(self._x + self._diameter / 2 + distance * math.sin(angle)),
                               int(self._y + self._diameter / 2 + distance * math.cos(angle)))

                end_point = (int(self._x + self._diameter / 2 + self._diameter / 2 * math.sin(angle)),
                             int(self._y + self._diameter / 2 + self._diameter / 2 * math.cos(angle)))

                pygame.draw.line(surface,
                                 RadarView.RED,
                                 start_point,
                                 end_point,
                                 1)
        # Граница обзора
        pygame.draw.arc(surface,
                        RadarView.GREEN,
                        pygame.Rect(self._x, self._y, self._diameter, self._diameter),
                        math.radians(30),
                        math.radians(150),
                        2)

        # Запрещенная зона
        pygame.draw.arc(surface,
                        RadarView.WHITE,
                        pygame.Rect(self._x + self._diameter / 2 - self._forbidden_radius,
                                    self._y + self._diameter / 2 - self._forbidden_radius,
                                    self._forbidden_radius * 2,
                                    self._forbidden_radius * 2),
                        math.radians(30),
                        math.radians(150),
                        2)

        # Левая граница обзор
        pygame.draw.line(surface,
                         RadarView.GREEN,
                         (self._x + self._diameter / 2,
                          self._y + self._diameter / 2),
                         (self._x + self._diameter / 2 + self._diameter / 2 * math.sin(math.radians(120)),
                          self._y + self._diameter / 2 + self._diameter / 2 * math.cos(math.radians(120))),
                         2)
        # Правая граница обзора
        pygame.draw.line(surface,
                         RadarView.GREEN,
                         (self._x + self._diameter / 2,
                          self._y + self._diameter / 2),
                         (self._x + self._diameter / 2 + self._diameter / 2 * math.sin(math.radians(240)),
                          self._y + self._diameter / 2 + self._diameter / 2 * math.cos(math.radians(240))),
                         2)
        # Центральная линия
        pygame.draw.line(surface,
                         RadarView.GREEN,
                         (self._x + self._diameter / 2,
                          self._y + self._diameter / 2),
                         (self._x + self._diameter / 2,
                          self._y),
                         1)
