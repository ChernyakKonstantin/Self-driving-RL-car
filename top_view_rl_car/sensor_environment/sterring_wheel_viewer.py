import os
from typing import Tuple, Any

import pygame

from .abstract import GameObject, Resetable


class SteeringWheelViewer(GameObject, Resetable):
    def __init__(self, position: pygame.Vector2, orientation: float, size: Tuple = (50, 50)):
        self._position = position
        self._orientation = orientation
        self._size = size
        self._image = self._load_steering_wheel_image()

    def _load_steering_wheel_image(self) -> pygame.Surface:
        base_path = os.path.dirname(__file__)
        sprite_path = os.path.join(base_path, "assets", "steering_wheel.png")
        image = pygame.image.load(sprite_path).convert_alpha()
        image = pygame.transform.scale(image, self._size)
        return image

    def update(self, delta_alpha: float) -> None:
        self._orientation += delta_alpha

    def show(self, surface: Any) -> None:
        image = pygame.transform.rotate(self._image, self._orientation)
        surface.blit(image, dest=self._position)

    def reset(self, *args, **kwargs):
        self._orientation = 0
