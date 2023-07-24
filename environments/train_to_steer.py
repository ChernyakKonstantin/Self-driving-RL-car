from typing import Tuple, Dict, Sequence, Any

import gym
import gymnasium as gym
import numpy as np
# from gymnasium import spaces
from gym import spaces
from .godot_client import GodotClient
import cv2


class TrainToSteerEnv(gym.Env):
    """Wrapper to handle GODOT any other side simulators with same interface."""

    def __init__(
        self,
        image_size: Sequence[int],
        engine_client: GodotClient,
        wheel_rotation_limit_per_step: Tuple[float, float] = (-10., 10.),
        n_frames_to_stack: int = 4,
        reward_values: Dict[str, float] = {
            "penalty": -100., "encouragement": 1.},
    ):
        """
        image_size: Sequence of [n_frames, width, height, num_channels].
        reward_values: Dictionary with keys `penalty`, `encouragement`.
        * `penalty` is given if the agent colides an obstacle,
        * `encouragement` is given each step the agent successfully drives.
        """
        super().__init__()
        # RL agent can implement its own observed data preprocessing.
        self.observation_space = spaces.Dict(
            # Degrees. A steering wheel can be rotated two rounds to each side.
            spaces={
                "wheel_position": spaces.Box(
                    low=-720,
                    high=720,
                ),
                "frames": spaces.Box(
                    low=0,
                    high=255,
                    shape=image_size,
                    dtype=np.uint8
                )
            },
        )
        # TODO: implement action space (pre)processing if required.
        self.action_space = spaces.Box(
            *wheel_rotation_limit_per_step,
            box=[1,],
            dtype=np.float32,
        )

        self.engine_client = engine_client
        self.n_frames_to_stack = n_frames_to_stack

        self.reward_values = reward_values

        # Set during reset
        self.state = None

    def reward_function(self, is_crashed: bool) -> float:
        if is_crashed:
            return self.reward_values["penalty"]
        else:
            return self.reward_values["encouragement"]

    def get_current_state(self, action: np.ndarray) -> Dict[str, Any]:
        # TODO: probably needs to know distance to closest obstacle for reward shaping
        self.engine_client.send_action({"wheel_delta": action}) # TODO: not forget while implementing GODOT
        frames = np.vstack([self.engine_client.request_frame()
                           for _ in self.n_frames_to_stack])
        wheel_position = self.engine_client.request_wheel_position()
        is_crashed = self.engine_client.request_is_crashed()
        current_state = {
            "frames": frames,
            "wheel_position": wheel_position,
            "is_crashed": is_crashed,
        }
        return current_state

    def step(self, action: np.ndarray) -> Tuple[np.ndarray, float, bool, dict]:
        """Action is mask where 1 denotes a selected label."""
        self.state: Dict[str, Any] = self.get_current_state(action)
        done = self.state.pop("is_crashed")
        reward = self.reward_function(is_crashed=done)
        info = {}  # TODO if there is extra info to include
        observation = self.observe(self.state)
        return observation, reward, done, info

    def observe(self, state: Dict[str, Any]) -> Dict[str, Any]:
        observation = {key: state[key]
                       for key in self.observation_space.keys()}
        return observation

    def reset(self) -> np.ndarray:
        self.state = self.engine_client.reset()
        observation = self.observe(self.state)
        return observation

    def render(self):
        # TODO: check if works correctly
        cv2.imshow("Current frame", self.state["frames"][-1])
        if cv2.waitKey(0) & 0xFF == ord('q'):
            cv2.destroyAllWindows()

    def close(self):
        cv2.destroyAllWindows()

    def action_masks(self) -> Any:
        raise NotImplementedError

    def seed(self, *args, **kwargs):
        # TODO: Find why we need it
        pass
