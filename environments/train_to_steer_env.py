from typing import Tuple, Dict, List, Any

import numpy as np
from gymnasium import spaces
from godot_gym_api import GodotEnvironment
from .enums import Request

class TrainToSteerEnv(GodotEnvironment):
    """Wrapper to handle GODOT or any other side simulators with same interface."""

    def __init__(
        self,
        protobuf_message_module,
        engine_address: Tuple[str, int] = ("127.0.0.1", 9090),
        engine_chunk_size: int = 65536,
        wheel_rotation_limit_per_step: Tuple[float, float] = (-1 / 60, 1/60),  # TODO: move to configuration of GODOT app
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
                "parking_sensors": spaces.Box(
                    low=0,
                    high=2,
                    shape=[8, self.repeat_action],  # TODO: pull first element from env.
                    dtype=np.float32,
                )
            },
        )
        self.action_space = spaces.Box(
            low=-1,
            high=1,
            shape=[1,],
            dtype=np.float32,
        )

        # Set during reset
        self.step_counter = None

        # Initialized during first use. Ensures that observations are consistent.
        self.key_order: Dict[str, List[str]] = {}

        # Must be initialized before `super().__init__` call.
        self.requested_observation = [
            Request.WHEEL_POSITION,
            Request.PARKING_SENSORS,
            Request.IS_CRASHED,
        ]
        super().__init__(protobuf_message_module, engine_address, engine_chunk_size)

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
        """The environment does not support truncation."""
        state = self._godot_step(action.item())
        self.step_counter += 1
        observation = self._observe(state)
        terminated = self._get_is_terminated(state["is_crashed"])
        reward = self.reward_function(observation["parking_sensor"], state["is_crashed"])
        return observation, reward, terminated, False, {}

    def observe(self, state: Dict[str, Any]) -> Dict[str, Any]:
        return {k: state[self.AGENT_KEY][k] for k in self.observation_space.keys()}

    def reset(self, *args, **kwargs) -> np.ndarray:
        self._step_counter = 0
        state = self._godot_reset()
        observation = self._observe(state)
        return observation, {}

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
