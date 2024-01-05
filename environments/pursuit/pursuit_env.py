import gymnasium as gym
from math import pi
import numpy as np
from .car import Car
from .world import World
from typing import Dict
import cv2
import sys
from scipy import spatial


class PursuitEnv(gym.Env):
    SEED = 0

    def __init__(
        self,
        car_config: Dict[str, float] = {},
        world_config: Dict[str, float] = {},
        dt: float = 1 / 30,  # s
        timeout: float = 60,  # s
        render: bool = False,
    ):
        self.world = World(**world_config)
        self.car = Car(**car_config)

        self.dt = dt
        self.timeout = timeout
        self.render_ = render

        self.observation_space = gym.spaces.Dict(
            {
                "tgt_x": gym.spaces.Box(0, self.world.width, [1], np.float32),
                "tgt_y": gym.spaces.Box(0, self.world.width, [1], np.float32),
                "x": gym.spaces.Box(0, self.world.width, [1], np.float32),
                "y": gym.spaces.Box(0, self.world.height, [1], np.float32),
                "orientation": gym.spaces.Box(*self.car.orientation_range, [1], np.float32),
                "velocity": gym.spaces.Box(self.car.max_speed_rear, self.car.max_speed_forward, [1], np.float32),
                "steering": gym.spaces.Box(-self.car.max_steering, self.car.max_steering, [1], np.float32),
                "acceleration": gym.spaces.Box(self.car.max_deceleration, self.car.max_acceleration, [1], np.float32),
            }
        )
        # Deceleration / Acceleration and Steering velocity. Both are relative.
        self.action_space = gym.spaces.Box(-1, 1, [2], dtype=np.float32)

        self.time: float
        self.n_steps: int

    def get_next_state(self) -> Dict[str, np.ndarray]:
        next_state = {}
        car_state = self.car.get_state()
        tgt_state = self.world.get_state()
        next_state.update(car_state)
        next_state.update(tgt_state)
        return next_state

    def reward_function(self, collided: bool, target_reached: bool) -> float:
        # Agent should move towards the target.
        reward1 = -self.world.get_distance_to_target(self.car.x, self.car.y) / self.world.max_distance_to_target
        if collided:
            # Agent should avoid collisions.
            reward2 = -100
        elif target_reached:
            # Agent should stop at the target
            if self.car.velocity > 0:
                reward2 = -self.car.velocity / self.car.max_speed_forward
            else:
                reward2 = -self.car.velocity / self.car.max_speed_rear
        else:
            reward2 = 0
        reward = reward1 + reward2
        return reward

    def step(self, action):
        acceleration = action[0]
        steering_speed = action[1]
        self.car.step(self.dt, acceleration, steering_speed)
        collided = self.world.maybe_handle_collison(self.car)

        truncated = self.time >= self.timeout
        self.time += self.dt
        self.n_steps += 1

        next_state = self.get_next_state()

        target_reached = self.world.is_target_reached(self.car.x, self.car.y)
        terminated = target_reached or collided

        reward = self.reward_function(collided, target_reached)

        info = {
            "simultator_time": self.time,
            "simulator_step": self.n_steps,
        }
        if self.render_:
            self.render()
        return next_state, reward, terminated, truncated, info


    def reset(self, options=None, seed=SEED):
        self.time = 0.0
        self.n_steps = 0
        self.world.reset()
        self.car.reset(initial_x=self.world.width / 2, initial_y=self.world.height / 2)
        next_state = self.get_next_state()
        return next_state, {}

    def render(self):
        MARGIN = 10
        CAR_SIZE = 1
        TARGET_SIZE = 1
        RESIZED_FRAME = [400, 400]

        image_shape = (self.world.height, self.world.width, 3)
        image = np.full(image_shape, 255, dtype=np.uint8)
        top_left = (0, 0)
        top_right = (self.world.width, 0)
        bottom_left = (0, self.world.height)
        bottom_right = (self.world.width, self.world.height)
        cv2.line(image, top_left, top_right, color=(0, 0, 0), thickness=2)
        cv2.line(image, top_right, bottom_right, color=(0, 0, 0), thickness=2)
        cv2.line(image, bottom_right, bottom_left, color=(0, 0, 0), thickness=2)
        cv2.line(image, bottom_left, top_left, color=(0, 0, 0), thickness=2)

        cv2.circle(
            image,
            (int(round(self.world.tgt_x)), int(round(self.world.tgt_y))),
            TARGET_SIZE + self.world.catch_radius,
            (0, 255, 0, 20),
            -1,
        )
        cv2.circle(image, (int(round(self.world.tgt_x)), int(round(self.world.tgt_y))), TARGET_SIZE, (0, 0, 255), -1)

        car_front_left = (self.car.wheel_base, -1)
        car_front_right = (self.car.wheel_base, 1)
        car_rear_left = (0, -1)
        car_rear_right = (0, 1)
        rot = np.asarray(
            [
                [np.cos(self.car.orientation), -np.sin(self.car.orientation)],
                [np.sin(self.car.orientation), np.cos(self.car.orientation)],
            ]
        )
        points = np.asarray([car_front_left, car_front_right, car_rear_left, car_rear_right])
        points = (rot @ points.T).T
        points += np.asarray([[self.car.x, self.car.y]])
        points = np.round(points).astype(int)
        car_front_left, car_front_right, car_rear_left, car_rear_right = points
        cv2.line(image, car_front_left, car_front_right, (255, 0, 0), 1)
        cv2.line(image, car_front_right, car_rear_right, (255, 0, 0), 1)
        cv2.line(image, car_rear_right, car_rear_left, (255, 0, 0), 1)
        cv2.line(image, car_rear_left, car_front_left, (255, 0, 0), 1)

        cv2.circle(image, (int(round(self.car.x)), int(round(self.car.y))), CAR_SIZE, (255, 255, 0), -1)

        frame_shape = (self.world.height + MARGIN * 2, self.world.width + MARGIN * 2, 3)
        frame = np.full(frame_shape, 255, dtype=np.uint8)
        frame[MARGIN:-MARGIN, MARGIN:-MARGIN, :] = image
        frame = cv2.resize(frame, RESIZED_FRAME)
        cv2.imshow("Visualization", frame)
        if cv2.waitKey(25) & 0xFF == ord("q"):
            self.close()

    def close(self):
        cv2.destroyAllWindows()
