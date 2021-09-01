# TODO Придумать нормальную генерацию уровней
# TODO Реализовать бесконечный уровень


# TODO: наблюдение - 1 кадр. Пускай какой-нибудь wrapper занимается стакингом

from typing import Any, List, Tuple

import numpy as np
import pygame
from gym import core, spaces

from .action_detector import ActionDetector
from .car import Car
from .colision_detector import ColisionDetector
from .colors import Colors
from .world import World


class Environment(core.Env):
    """
    Мир со случайно генерируемой бесконечной дорогой.

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
    _INIT_CAR_Y = 10
    # Параметры трассы
    _ROAD_WIDTH = 50  # TODO: Needed to be removed
    _START_WALL_X = int(round(_INIT_CAR_X - _ROAD_WIDTH / 2))
    _START_WALL_Y = 5

    # Параметры завершения эпизода
    _NO_ACTION_LIMIT = 3
    _MIN_DISTANCE_TO_OBSTACLE = 5
    # Параметры награды
    LOOSE_REWARD = -130

    metadata = {'render.modes': ['human', ]}

    # TODO: оформить константами
    action_space = spaces.Dict({
        'steering': spaces.Box(low=-45.0, high=45.0, shape=(), dtype=np.float32),
        'velocity': spaces.Box(low=-2, high=2, shape=(), dtype=np.float32),
    })

    observation_space = spaces.Dict({
        'steering': spaces.Box(low=-45.0, high=45.0, shape=(), dtype=np.float32),
        'velocity': spaces.Box(low=-3.0, high=8.0, shape=(), dtype=np.float32),
        'distance': spaces.Box(low=0.0, high=200.0, shape=(30, 1), dtype=np.float32),
    })

    def __init__(self):
        self._colision_detector = ColisionDetector(Environment._MIN_DISTANCE_TO_OBSTACLE)
        self._action_detector = ActionDetector(limit=Environment._NO_ACTION_LIMIT)
        self._world = World(Environment._START_WALL_X, Environment._START_WALL_Y, Environment._WORLD_LENGTH)
        self._car = Car(Environment._INIT_CAR_X, Environment._INIT_CAR_Y)
        self._car.attach(self._action_detector)
        self._car_prev_pos = Environment._INIT_CAR_Y
        pygame.init()
        self._surface = pygame.display.set_mode(Environment._SURFACE_SIZE)
        self._next_observation = None

        self.clock = pygame.time.Clock()

    # _____Private_methods_____

    def reset(self) -> list:
        # self._colision_detector.reset()
        self._action_detector.reset()
        self._car.reset()
        self._world.reset()
        self._car_prev_pos = Environment._INIT_CAR_Y  # TODO: move to Car class
        self._next_observation = self._get_observation()
        return self._next_observation

    def _get_observation(self) -> list:
        filtered_walls = self._car.sensor.filter_obstacles(self._world.walls)
        return self._car.sensor.get_view(filtered_walls)

    def _get_reward(self) -> float:
        reward = self._car.y - self._car_prev_pos
        self._car_prev_pos = self._car.y
        return reward

    # _____Public_methods_____

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
        is_done = False  # self._colision_detector.check(self._observation) or self._action_detector()
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
        self._car.sensor.show(self._surface)
        pygame.display.flip()

    def close(self) -> None:
        pygame.quit()

    def seed(self, seed=None) -> List[int]:
        raise NotImplementedError
