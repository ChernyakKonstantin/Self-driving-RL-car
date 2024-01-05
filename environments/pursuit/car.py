import math
from typing import Dict, Union
import numpy as np


class Car:
    """Bicycle model of four-wheeled car with front wheel for steering."""
    def __init__(
            self,
            wheel_base: float = 2.4,  # m
            max_steering: float = np.pi/3,  # radians/s
            max_steering_speed: float = np.pi/3,  # radians/s
            max_speed_forward: float = 27.8,  # m/s
            max_speed_rear: float = -2.4,  # m/s
            max_acceleration: float = 2.78,  # m/s^2
            max_deceleration: float = -2,  # m/s^2
        ):
        self.wheel_base = wheel_base
        self.max_steering = max_steering
        self.max_steering_speed = max_steering_speed
        self.max_speed_forward = max_speed_forward
        self.max_speed_rear = max_speed_rear
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.orientation_range = (-2*math.pi, 2*math.pi)
        self.x: float  # m
        self.y: float  # m
        self.velocity: float  # m/s
        self.steering: float  # rad
        self.orientation: float  # rad
        self.acceleration: float  # m/s^2
        self.reset()

    def reset(
            self,
            initial_x: float = 0.,
            initial_y: float = 0,
            initial_velocity: float = 0.,
            initial_steering: float = 0.,
            initial_orientation: float = 0.,
        ):
        self.x = initial_x
        self.y = initial_y
        self.velocity = initial_velocity
        self.steering = initial_steering
        self.orientation = initial_orientation
        self.acceleration = 0.

    def get_state(self) -> Dict[str, float]:
        state = {
            "x": [self.x,],
            "y": [self.y,],
            "orientation": [self.orientation,],
            "velocity": [self.velocity,],
            "steering": [self.steering,],
            "acceleration" : [self.acceleration,]
        }
        return state

    def step(self, dt: float, acceleration: float, steering_speed: float):

        if acceleration < 0:
            acceleration = abs(acceleration) * self.max_deceleration
        else:
            acceleration *= self.max_acceleration
        steering_speed *= self.max_steering_speed

        self.acceleration = acceleration
        d_steering = steering_speed * dt
        self.steering = np.clip(self.steering + d_steering, -self.max_steering, self.max_steering)

        d_velocity = acceleration * dt
        d_orientation = self.velocity * np.tan(self.steering) / self.wheel_base
        d_x = self.velocity * np.cos(self.orientation)
        d_y = self.velocity * np.sin(self.orientation)

        self.velocity = np.clip(self.velocity + d_velocity, self.max_speed_rear, self.max_speed_forward)
        self.orientation += d_orientation
        self.orientation = np.sign(self.orientation) * (abs(self.orientation) % (2 * math.pi))

        self.x += d_x
        self.y += d_y
