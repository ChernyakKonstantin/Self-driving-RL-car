# TODO Придумать нормальную генерацию уровней
# TODO Реализовать бесконечный уровень
import random
from typing import Tuple

import numpy as np
import pygame

from action_detector import ActionDetector
from car import Car
from colors import Colors
from obstacle import Line
from sensor import Sensor


class Environment:
    # Размеры мира
    _WORLD_LENGTH = 650
    _WORLD_WIDTH = 300
    _SURFACE_SIZE = _WORLD_WIDTH + 50, _WORLD_LENGTH + 50
    # Начальное положение объекта управления
    _INIT_CAR_X = _WORLD_WIDTH / 2
    _INIT_CAR_Y = 10
    # Параметры трассы
    _ROAD_WIDTH = 50
    _START_WALL_X = _INIT_CAR_X - _ROAD_WIDTH / 2
    _START_WALL_Y = 5
    _WALL_X_SHIFT = 15
    _WALL_Y_SHIFT = 30
    # Параметры завершения эпизода
    _NO_ACTION_LIMIT = 3
    _MIN_DISTANCE_TO_OBSTACLE = 5
    # Параметры награды
    LOOSE_REWARD = -130

    @staticmethod
    def get_observation_shape():
        return Sensor.get_observation_shape()

    @property
    def actions(self) -> dict:
        return self._actions

    def __init__(self, n_steps: int = 4):
        """
        Args:
            n_steps (int): Число повторений действия в рамках одного шага. 
        """
        self._n_steps = n_steps

        self._initialize()

        self._actions = {
            0: [],  # Ехать по инерции
            1: [0],  # Ехать прямо
            2: [1],  # Ехать влево
            3: [2],  # Ехать вправо
            4: [0, 1],  # Ехать прямо и влево
            5: [0, 2],  # Ехать прямо и вправо
            6: [3],  # Затормозить
        }

        pygame.init()
        self._surface = pygame.display.set_mode(Environment._SURFACE_SIZE)

    def _initialize(self):
        self.car = Car(Environment._INIT_CAR_X, Environment._INIT_CAR_Y)
        self._action_detector = ActionDetector(limit=Environment._NO_ACTION_LIMIT)
        self.car._attach(self._action_detector)

        self.walls = []
        self._generate_world()
        self.car_prev_pos = Environment._INIT_CAR_Y
        self.observation = None
        self.next_observation = None

    def _generate_world(self) -> None:
        first_point = (Environment._START_WALL_X, Environment._START_WALL_Y)
        while first_point[1] < Environment._WORLD_LENGTH:
            second_point_x = first_point[0] + random.choice([-1, 1]) * random.randint(0, Environment._WALL_X_SHIFT)
            second_point_y = first_point[1] + random.randint(0, Environment._WALL_Y_SHIFT)
            second_point = (second_point_x, second_point_y)
            self.walls.append(Line(*first_point, *second_point))
            first_point = second_point
        n_walls = len(self.walls)
        for index in range(n_walls):
            self.walls.append(self.walls[index].shifted_copy(Environment._ROAD_WIDTH))

        # Верхняя граница
        self.walls.append(Line(*(0, Environment._START_WALL_Y),
                               *(Environment._WORLD_LENGTH, Environment._START_WALL_Y)))

        # Нижняя граница
        self.walls.append(Line(*(0, Environment._WORLD_LENGTH),
                               *(Environment._WORLD_LENGTH, Environment._WORLD_LENGTH)))

    def _get_observation(self) -> list:
        return self.car.sensor.get_view(self.walls)

    def _collided(self, observation: list) -> bool:
        if min(observation) < Environment._MIN_DISTANCE_TO_OBSTACLE:
            return True
        else:
            return False

    def _get_reward(self) -> float:
        reward = self.car.y - self.car_prev_pos
        self.car_prev_pos = self.car.y
        return reward

    def _step(self, action) -> Tuple[list, float, bool, None]:
        """Метод однократного совершения действия."""
        self.observation = self.next_observation
        if not self._collided(self.observation):
            self.car.move(action)
            self.next_observation = self._get_observation()
            reward = self._get_reward()
            is_done = False  # self._action_detector()
        else:
            self.next_observation = self._get_observation()
            reward = Environment.LOOSE_REWARD
            is_done = True
        return self.next_observation, reward, is_done, None  # None, т.к. environment не возвращает доп.информации

    def get_action_list(self, action_id: int) -> list:
        return self._actions[action_id]

    def reset(self) -> np.ndarray:
        self._initialize()
        self.next_observation = self._get_observation()
        return np.vstack([self.next_observation for _ in range(self._n_steps)])

    def step(self, action) -> Tuple[np.ndarray, float, bool, None]:
        """
        Метод совершения многокартного числа шагов с одним и тем же действием.
        Эмулирует реального игрока, т.к. нажатие клавиши длится несколько циклов программы.
        """
        next_observations = []
        rewards = []
        is_dones = []
        for _ in range(self._n_steps):
            next_observation, reward, is_done, _ = self._step(action)
            next_observations.append(next_observation)
            rewards.append(reward)
            is_dones.append(is_done)
        next_observation = np.vstack(next_observations)
        reward = np.sum(rewards).item()
        is_done = is_dones[-1] or self._action_detector()
        return next_observation, reward, is_done, None

    def sample_action(self) -> int:
        return np.random.choice(len(self._actions))

    def is_closed(self) -> bool:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True

    def render(self) -> None:
        self._surface.fill(Colors.BLACK)
        for wall in self.walls:
            wall.show(self._surface)
        self.car.sensor.show(self._surface)
        pygame.display.flip()

    def quit(self):
        pygame.quit()
