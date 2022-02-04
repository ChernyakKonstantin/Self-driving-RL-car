from typing import Any, List, Tuple

import numpy as np
import pygame
from gym import core, spaces

from .action_detector import ActionDetector
from .car import Car
from .colision_detector import ColisionDetector
from .colors import Colors
from .world import World

import time

class Environment(core.Env):
    """
    Мир со случайно генерируемой дорогой.

    Действия:
    * Изменить угол поворота руля: float
    * Изменить скорость движения: float

    Наблюдения:
    * Текущий угол поворота руля (градусы): float
    * Текущая скорость: float
    * Данные с датчика расстояния: np.ndarray of float
    """

    # Размеры мира
    _WORLD_LENGTH = 650
    _WORLD_WIDTH = 300
    _SURFACE_SIZE = _WORLD_WIDTH + 50, _WORLD_LENGTH + 50
    # Начальное положение объекта управления
    _INIT_CAR_X = _WORLD_WIDTH / 2
    _INIT_CAR_Y = 30
    # Параметры трассы
    _ROAD_WIDTH = 100
    _START_WALL_X = int(round(_INIT_CAR_X - _ROAD_WIDTH / 2))
    _START_WALL_Y = 5

    # Параметры завершения эпизода
    _NO_ACTION_LIMIT = 10
    _MIN_DISTANCE_TO_OBSTACLE = 1
    # Параметры награды
    LOOSE_REWARD = -1

    metadata = {'render.modes': ['human', ]}

    action_space = spaces.Dict({
        'steering': spaces.Box(low=Car.MIN_STEERING_ANGLE, high=Car.MAX_STEERING_ANGLE, shape=(1,), dtype=np.float32),
        'velocity': spaces.Box(low=Car.MIN_SPEED, high=Car.MAX_SPEED, shape=(1,), dtype=np.float32),
    })

    observation_space = spaces.Dict({
        'steering': spaces.Box(low=Car.MIN_STEERING_ANGLE, high=Car.MAX_STEERING_ANGLE, shape=(), dtype=np.float32),
        'velocity': spaces.Box(low=Car.MIN_SPEED, high=Car.MAX_SPEED, shape=(), dtype=np.float32),
        'distance': spaces.Box(low=0.0, high=200.0, shape=(30, 1), dtype=np.float32),
    })

    def __init__(self):
        self._world = World(Environment._START_WALL_X, Environment._START_WALL_Y, Environment._WORLD_LENGTH)
        self._car = Car(Environment._INIT_CAR_X, Environment._INIT_CAR_Y)
        self._collision_detector = ColisionDetector((self._car.x, self._car.y),
                                                    self._car.SIZE,
                                                    Environment._MIN_DISTANCE_TO_OBSTACLE)
        self._action_detector = ActionDetector(limit=Environment._NO_ACTION_LIMIT)
        self._car.attach(self._collision_detector)
        self._car.attach(self._action_detector)
        pygame.init()
        self._surface = pygame.display.set_mode(Environment._SURFACE_SIZE)
        self._next_observation = None

    # _____Private_methods_____

    def _get_observation(self) -> list:
        filtered_walls = self._car.sensor.filter_obstacles(self._world.walls)
        return self._car.sensor.get_view(filtered_walls)

    def _get_reward(self) -> float:
        return 0

    # _____Public_methods_____

    def reset(self) -> list:
        self._world.reset()
        self._collision_detector.reset(*self._world.to_points_array())
        self._action_detector.reset()
        self._car.reset()

        self._next_observation = self._get_observation()
        return self._next_observation

    def is_closed(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

    def step(self, action: Tuple[float, float]) -> Tuple[list, float, bool, Any]:
        """
        Action хранит в себе текущий угол поворота колес и скорость.
        TODO: Изменить на дельту.
        """
        self._observation = self._next_observation
        is_done = self._collision_detector.check() # or self._action_detector()
        if not is_done:
            steering_angle, velocity = action
            self._car.move(steering_angle, velocity)
            reward = self._get_reward()
        else:
            reward = Environment.LOOSE_REWARD
        self._next_observation = self._get_observation()
        # Дополнительная информация отсутсвует, но она необходима для интерфейса gym
        info = None
        return self._next_observation, reward, is_done, info

    def render(self, mode='human') -> None:
        """Параметр mode не используется, но необходим для интерфейса gym."""
        self._surface.fill(Colors.BLACK)
        self._world.show(self._surface)
        self._collision_detector.show(self._surface)
        self._car.show(self._surface)
        pygame.display.flip()

    def close(self) -> None:
        pygame.quit()

    def seed(self, seed=None) -> List[int]:
        raise NotImplementedError
