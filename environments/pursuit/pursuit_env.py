import gymnasium as gym
from math import pi
import numpy as np
from .car import Car
from .world import World
from typing import Dict
import cv2
import sys

class PursuitEnv(gym.Env):
    PIx2 = 2 * np.pi
    SEED = 0

    def __init__(
            self, 
            car_config: Dict[str, float] = {}, 
            world_config: Dict[str, float] = {},
            dt: float = 1/30,  # s
            timeout: float = 60, # s
        ):
        self.world = World(**world_config)
        self.car = Car(**car_config)

        self.dt = dt
        self.timeout = timeout

        self.observation_space = gym.spaces.Dict({
            "tgt_x": gym.spaces.Box(
               0,
                self.world.width,
                [1,], 
                np.float32,
            ),
            "tgt_y": gym.spaces.Box(
                0,
                self.world.width,
                [1,], 
                np.float32,
            ),
            "x": gym.spaces.Box(
                0,
                self.world.width,
                [1,], 
                np.float32,
            ),
            "y": gym.spaces.Box(
                0,
                self.world.height,
                [1,], 
                np.float32,
            ),
            "orientation": gym.spaces.Box(
                -self.PIx2, 
                self.PIx2, 
                [1,], 
                np.float32,
            ),
            "velocity": gym.spaces.Box(
                self.car.max_speed_rear,
                self.car.max_speed_forward,
                [1,],
                np.float32,
            ),
            "steering": gym.spaces.Box(
                -self.car.max_steering,
                self.car.max_steering,
                [1,],
                np.float32,
            ),
            "acceleration": gym.spaces.Box(
                self.car.max_deceleration,
                self.car.max_acceleration,
                [1,],
                np.float32,
            ),
        })

        self.action_space = gym.spaces.Box(-1, 1, [2,], dtype=np.float32)
          
        self.time: float
        self.n_steps: int

    def get_next_state(self):
        next_state = {}
        car_state = self.car.get_state()
        tgt_state = self.world.get_state()
        next_state.update(car_state)
        next_state.update(tgt_state)
        return next_state
    
    def step(self, action):
        acceleration = action[0]
        if acceleration < 0:
            acceleration = abs(acceleration) * self.car.max_deceleration
        else:
            acceleration *= self.car.max_acceleration

        steering_speed = action[1]
        steering_speed *= self.car.max_steering_speed

        truncated = self.time >= self.timeout
        self.time += self.dt
        self.n_steps += 1
        self.car.step(self.dt, acceleration, steering_speed)
        
        next_state = self.get_next_state()

        out_of_bounds = not (0 <= self.car.x <= self.world.width and 0 <= self.car.y <= self.world.height)
        position_matched = self.world.position_is_matched(self.car.x, self.car.y)    
        terminated = position_matched or out_of_bounds
        reward = -np.sqrt(np.square(np.array([self.car.x, self.car.y]) - np.array([self.world.tgt_x, self.world.tgt_y])).sum()).item()
        if out_of_bounds:
            reward -= 100
        info =  {
            "simultator_time": self.time,
            "simulator_step": self.n_steps,
        }
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
        
        cv2.circle(image, (int(round(self.world.tgt_x)), int(round(self.world.tgt_y))), TARGET_SIZE + self.world.catch_radius, (0, 255, 0, 20), -1)
        cv2.circle(image, (int(round(self.world.tgt_x)), int(round(self.world.tgt_y))), TARGET_SIZE, (0, 0, 255), -1)
        
        cv2.circle(image, (int(round(self.car.x)), int(round(self.car.y))), CAR_SIZE, (255, 0, 0), -1)
        
        frame_shape = (self.world.height + MARGIN * 2, self.world.width + MARGIN * 2, 3)
        frame = np.full(frame_shape, 255, dtype=np.uint8)
        frame[MARGIN:-MARGIN, MARGIN:-MARGIN, :] = image
        frame = cv2.resize(frame, RESIZED_FRAME)
        cv2.imshow("Visualization", frame)
        if cv2.waitKey(25) & 0xFF == ord('q'):
            self.close()

    
    def close(self):
        cv2.destroyAllWindows()