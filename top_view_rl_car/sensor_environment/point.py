import math

import pygame

from .abstract import GameObject


class Point(GameObject):
    """
    Dot is a basic object that forms lines.
    """

    def __init__(self, x: float, y: float, orientation: int):
        # orientation in degrees
        self.orientation = orientation
        self.position = pygame.Vector2(x, y)

    def show(self, surface):
        pygame.draw.circle(surface, (255, 255, 255), self.position, 2)
