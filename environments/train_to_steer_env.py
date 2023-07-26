from typing import Tuple, Dict, List, Any

import gym
import gymnasium as gym
import numpy as np
from gymnasium import spaces
from .godot_client import GodotClient
import cv2
from .godot_client.enums import Request
from functools import partial

class TrainToSteerEnv(gym.Env):
    """Wrapper to handle GODOT any other side simulators with same interface."""

    def __init__(
        self,
        engine_client: GodotClient,
        wheel_rotation_limit_per_step: Tuple[float, float] = (-1 / 60, 1/60),
        repeat_action: int = 4,
        reward_values: Dict[str, float] = {"penalty": -100., "encouragement": 1.},
        episode_length: int = 500,
        terminate_on_crash: bool = False,
    ):
        """
        image_size: Sequence of [n_frames, width, height, num_channels].
        reward_values: Dictionary with keys `penalty`, `encouragement`.
        * `penalty` is given if the agent colides an obstacle,
        * `encouragement` is given each step the agent successfully drives.
        """
        super().__init__()
        self.engine_client = engine_client
        self.repeat_action = repeat_action
        self.reward_values = reward_values
        self.episode_length = episode_length
        self.terminate_on_crash = terminate_on_crash

        # RL agent can implement its own observed data preprocessing.
        self.observation_space = spaces.Dict(
            spaces={
                "steering": spaces.Box(
                    low=-1,
                    high=1,
                    shape=[1,],
                    dtype=np.float32,
                ),
                "parking_sensor": spaces.Box(
                    low=0,
                    high=2,
                    shape=[8, self.repeat_action],  # TODO: pull first element from env
                    dtype=np.float32,
                )
            },
        )
        # TODO: implement action space (pre)processing if required.
        self.action_space = spaces.Box(
            *wheel_rotation_limit_per_step,
            shape=[1,],
            dtype=np.float32,
        )

        # Set during reset
        self.state = None
        self.step_counter = None

        # Initialized during first use. Ensures that observations are consistent.
        self.key_order: Dict[str, List[str]] = {}

        self.requested_observation = [
            Request.WHEEL_POSITION,
            Request.PARKING_SENSORS,
            Request.IS_CRASHED,
        ]
        self._request_godot_step = partial(
            self.engine_client.request_step,
            requested_observation=self.requested_observation,
        )
        self._request_godot_reset = partial(
            self.engine_client.reset,
            requested_observation=self.requested_observation,
        )

    def reward_function(self, parking_sensor_data: List[List[int]], is_crashed: bool) -> float:
        if self.terminate_on_crash and is_crashed:
            return self.reward_values["penalty"]
        else:
            # Dense reward to encourage agent get far from obstacles.
            return np.min(parking_sensor_data) * self.reward_values["encouragement"]

    def _get_is_terminated(self, is_crashed) -> bool:
        if self.terminate_on_crash:
            return is_crashed
        else:
            return self.step_counter >= self.episode_length

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        self.state: Dict[str, Any] = self._request_godot_step(action={"steering_delta": action.item()})
        observation = self.observe(self.state)
        terminated = self._get_is_terminated(self.state["is_crashed"])
        truncated = False  # The environment does not support truncation
        reward = self.reward_function(observation["parking_sensor"], self.state["is_crashed"])
        info = {}  # TODO if there is extra info to include
        self.step_counter += 1
        return observation, reward, terminated, truncated, info

    def observe(self, state: Dict[str, Any]) -> Dict[str, Any]:
        observation = {}
        for observation_name in self.observation_space.keys():
            observation_element = state[observation_name]
            # Handle dict-like observations like parking sensors or RGB-cameras.
            if isinstance(observation_element, dict):
                if observation_name not in self.key_order:
                    self.key_order[observation_name] = list(observation_element.keys())
                observation[observation_name] = [observation_element[k] for k in self.key_order[observation_name]]
            else:
                observation[observation_name] = observation_element
        return observation

    def reset(self, *args, **kwargs) -> np.ndarray:
        print(f"Reset is requested. Current step is: {self.step_counter}")
        self.step_counter = 0
        self.state: Dict[str, Any] = self._request_godot_reset()
        info = {}  # TODO if there is extra info to include
        observation = self.observe(self.state)
        return observation, info

    def render(self):
        # TODO: implement if required
        pass

    def close(self):
        # TODO: implement if required
        pass

    def action_masks(self) -> Any:
        raise NotImplementedError

    def seed(self, *args, **kwargs):
        # TODO: implement if required
        pass
