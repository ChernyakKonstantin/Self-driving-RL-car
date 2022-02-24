import sys
from typing import Any, List, Tuple, Union, Dict

import gym
import numpy as np
import pygame

from .car import Car
from .collision_detector import CollisionDetector
from .sensor_viewer import SensorViewer
from .world import World


class SensorEnvironment(gym.Env):
    """
    Мир со случайно генерируемой дорогой.

    Действия:
    * Изменить угол поворота руля: float

    Наблюдения:
    * Данные с датчика расстояния: np.ndarray of float
    * Текущая ориентация в мире
    """

    # Параметры награды
    metadata = {'render.modes': ['human', ]}

    def __init__(self, config):
        self._world = World(*config["window_size"],
                            40,
                            config["velocity"],
                            config["part_length"],
                            config["road_width"])

        init_x = config["window_size"][0] // 2
        init_y = config["window_size"][1] // 2
        orientation = 0  # Parallel to Y axis

        self._car = Car(init_x, init_y,
                        orientation,
                        config["velocity"],
                        config["steering_bounds"],
                        config["sprite_size"],
                        config["n_rays"],
                        config["angle_of_view"],
                        config["ray_length"],
                        )
        self._collision_detector = CollisionDetector(config["sprite_size"])

        self._setup_spaces(config)
        self._render = config["render"]

        self.state = None
        self.is_done = None
        self.counter = None
        self._car_orientation = None
        self._intermediate_reward = config["intermediate_reward"]
        self._loose_reward = config["loose_reward"]

        if self._render:
            pygame.init()
            self._surface = pygame.display.set_mode(config["window_size"])
            self._sensor_viewer = SensorViewer(pygame.Vector2(0, 0),
                                               config["n_rays"],
                                               max_distance=config["ray_length"])
        else:
            self._surface = None

    def _setup_spaces(self, config):
        obs_spaces = gym.spaces.Dict({
            "sensor_data": gym.spaces.Box(low=0.0,
                                          high=config["ray_length"],
                                          shape=(config["n_rays"],),
                                          dtype=np.float32),
            "orientation": gym.spaces.Box(low=-180,
                                          high=180,
                                          shape=(1,),
                                          dtype=np.float32),
        })
        self.observation_space = obs_spaces

        # Delta of angle to steer the wheel
        self.action_space = gym.spaces.Box(*config["steering_bounds"],
                                           shape=(1,),
                                           dtype=np.float32)

    def _update_orientation(self, angle_delta: Union[int, float]) -> None:
        orientation = self._car_orientation + angle_delta
        if orientation > 180:
            orientation = orientation - 360
        elif orientation < -180:
            orientation = orientation + 360
        self._car_orientation = orientation

    def _filter_non_visible(self) -> np.ndarray:
        condition_1 = self._world.obstacle_coordinates[3] < self._car._position.y
        condition_2 = self._world.obstacle_coordinates[1] > self._car._position.y + self._car.sensor._ray_length
        return np.invert(condition_1 | condition_2)

    def _get_observation(self) -> Dict:
        mask = self._filter_non_visible()
        sensor_data = self._car.sensor.get_view(self._world.obstacle_coordinates[:, mask])
        return {"sensor_data": sensor_data, "orientation": np.array([self._car_orientation])}

    def _get_reward(self) -> float:
        return 1

    def reset(self) -> Dict:
        self._world.reset()
        self._car.reset(self._world._world_width // 2, self._world._world_length // 2, 0)
        self.counter = 0
        self._car_orientation = self._car._orientation
        self.is_done = False
        self.state = self._get_observation()
        return self.state

    def is_closed(self) -> bool:
        if self._render:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True

    def step(self, action: np.ndarray) -> Tuple[Dict, float, bool, Any]:
        """
        The method change the car orientation with "action" value that is change of the steering angle
        Args: Change of the car steering angle.

        Returns: Observation, reward, episode completion flag, additional information.
        """
        self._world.translate(action.item(), self._car._position)
        self._update_orientation(action.item())
        self.state = self._get_observation()
        self.is_done = self._collision_detector.check(self.state["sensor_data"])

        if self.is_done:
            reward = self._loose_reward
        else:
            reward = self._intermediate_reward

        # Currently there is no additional info, required by Gym.
        info = {}
        self.counter += 1
        if self._render:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
            # Without the call the windows freezes when no focus.
            pygame.event.pump()
            self.render()
        return self.state, reward, self.is_done, info

    def render(self, mode='human') -> None:
        """Параметр mode не используется, но необходим для интерфейса gym."""
        if self._render:
            self._sensor_viewer.update(self.state["sensor_data"])

            self._surface.fill(pygame.Color("black"))
            self._world.show(self._surface)
            self._car.show(self._surface)
            self._sensor_viewer.show(self._surface)
            pygame.display.flip()

    def close(self) -> None:
        pygame.quit()

    def seed(self, seed=None) -> List[int]:
        raise NotImplementedError
