from typing import Tuple

import gym
import gymnasium as gym
import numpy as np
# from gymnasium import spaces
from gym import spaces


class SteeringOnlyEnvironment(gym.Env):
    # Wrapper to handle GODOT any other side simulators with same interface.
    def __init__(self):
        super().__init__()
        self.observation_space = None  # TODO
        self.action_space = None  # TODO

        self.observation = None

    def reward_function(self) -> float:
        raise NotImplementedError

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        """Action is mask where 1 denotes a selected label."""
        raise NotImplementedError
        return self.observation, reward, done, info

    def reset(self) -> np.ndarray:
        raise NotImplementedError
        return self.observation

    def render(self):
        "No render method implemented for the environment."
        pass

    def close(self):
        "No close method implemented for the environment."
        pass

    def action_masks(self) -> Any:
        raise NotImplementedError

    def seed(self, *args, **kwargs):
        # TODO: Find why we need it
        pass
