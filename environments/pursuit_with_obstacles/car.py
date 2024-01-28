import math
from typing import Dict, Sequence
import numpy as np
from .proxemity_sensor import ProxemitySensor
from .detectable import Detectable


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
            max_sensor_distance: float = 40,
            n_sensors: int = 19,
            sensors_angle_range: tuple = (-np.pi/3, np.pi/3),
        ):
        self.max_sensor_distance = max_sensor_distance
        self.n_sensors = n_sensors
        self.sensors_angle_range = sensors_angle_range
        self.sensors = []
        for angle in np.linspace(*sensors_angle_range, n_sensors):
            self.sensors.append(ProxemitySensor(np.array([wheel_base, 0]), angle, max_sensor_distance))

        self.wheel_base = wheel_base
        self.max_steering = max_steering
        self.max_steering_speed = max_steering_speed
        self.max_speed_forward = max_speed_forward
        self.max_speed_rear = max_speed_rear
        self.max_acceleration = max_acceleration
        self.max_deceleration = max_deceleration
        self.orientation_range = (-math.pi, math.pi)
        self.angular_speed_range = (
            self.max_speed_rear * np.tan(self.max_steering) / self.wheel_base / (1/30), # TODO: Hardcoded delta_t
            self.max_speed_forward * np.tan(self.max_steering) / self.wheel_base / (1/30), # TODO: Hardcoded delta_t
        )
        self.max_centrifugal_force_amplitude_forward = self.centrifugal_force_amplitude(
            self.max_speed_forward,
            self.max_steering,
        )
        self.max_centrifugal_force_amplitude_rear = self.centrifugal_force_amplitude(
            self.max_speed_rear,
            self.max_steering,
        )
        self.x: float  # m
        self.y: float  # m
        self.velocity: float  # m/s
        self.steering: float  # rad
        self.steering_speed: float  # rad
        self.orientation: float  # rad
        self.acceleration: float  # m/s^2
        self.angular_speed: float  # rad/s
        self.reset()

    def reset(
            self,
            initial_x: float = 0.,
            initial_y: float = 0,
            initial_velocity: float = 0.,
            initial_steering: float = 0.,
            initial_steering_speed: float =0.,
            initial_orientation: float = 0.,
            initial_acceleration: float = 0.0,
        ):
        self.x = initial_x
        self.y = initial_y
        self.velocity = initial_velocity
        self.steering = initial_steering
        self.steering_speed = initial_steering_speed
        self.orientation = initial_orientation
        self.acceleration = initial_acceleration
        self.angular_speed = self.velocity * np.tan(self.steering) / self.wheel_base / (1/30)  # TODO: Hardcoded delta_t

    def get_state(self, obstacles: Sequence[Detectable]) -> Dict[str, float]:
        state = {
            "x": [self.x,],
            "y": [self.y,],
            "orientation": [self.orientation,],
            "velocity": [self.velocity,],
            "steering": [self.steering,],
            "angular_speed": [self.angular_speed,],
            "distances": [min([s.get_distance(o) for o in obstacles]) for s in self.sensors],
        }
        return state

    def step(self, dt: float, acceleration: float, steering_speed: float):

        if acceleration < 0:
            acceleration = abs(acceleration) * self.max_deceleration
        else:
            acceleration *= self.max_acceleration
        steering_speed *= self.max_steering_speed

        self.acceleration = acceleration
        self.steering_speed = steering_speed

        d_steering = steering_speed * dt
        self.steering = np.clip(self.steering + d_steering, -self.max_steering, self.max_steering)

        d_velocity = acceleration * dt
        d_orientation = self.velocity * np.tan(self.steering) / self.wheel_base
        self.angular_speed = d_orientation / (1/30) # TODO: Hardcoded delta_t

        d_x = self.velocity * np.cos(self.orientation)
        d_y = self.velocity * np.sin(self.orientation)

        self.velocity = np.clip(self.velocity + d_velocity, self.max_speed_rear, self.max_speed_forward)
        self.orientation += d_orientation

        # Change from commented below
        if self.orientation > math.pi:
            self.orientation -= 2 * math.pi
        elif self.orientation < -math.pi:
            self.orientation += 2 * math.pi
        # self.orientation = np.sign(self.orientation) * (abs(self.orientation) % (2 * math.pi))

        self.x += d_x
        self.y += d_y

        for sensor in self.sensors:
            sensor.update(np.array([d_x, d_y]), d_orientation)

    def centrifugal_force_amplitude(self, velocity: float = None, steering: float = None) -> float:
        if velocity is None:
            velocity = self.velocity
        if steering is None:
            steering = self.steering
        return abs(velocity ** 2 * math.tan(steering) / self.wheel_base)