import math
from typing import Tuple, Dict, Any
from scipy import spatial
import numpy as np

class DeterministicController:
    def __init__(self, car):
        self.car = car

    def _calc_steering(self, delta_angle: float, distance: float):
        return math.atan(2 * self.car.wheel_base * math.sin(delta_angle) / distance)

    def predict(self, obs: Dict[str, Any]):
        tgt_x = obs["tgt_x"][0][0]
        tgt_y = obs["tgt_y"][0][0]
        distance = spatial.distance.euclidean(
            (self.car.x, self.car.y),
            (tgt_x, tgt_y),
        )

        v = np.array([[1, 0]])
        rot = [[math.cos(self.car.orientation), -math.sin(self.car.orientation)], [math.sin(self.car.orientation), math.cos(self.car.orientation)]]
        v = (rot @ v.T).T[0]
        v2 = np.array([tgt_x - self.car.x, tgt_y - self.car.y])
        v2 /= np.linalg.norm(v2)
        angle = math.acos((v*v2).sum() / np.sqrt(v[0] ** 2 + v[1] ** 2) / np.sqrt(v2[0] ** 2 + v2[1] ** 2))
        sign = np.cross(v, v2).item()
        steering = self._calc_steering(angle, distance)
        steering *= sign
        steering_normed = steering / self.car.max_steering
        return steering_normed
        # steering_velocity_normed = (steering - obs["steering"][0][0]) / self.car.max_steering_speed
        # if steering_velocity_normed < 0:
        #     steering_velocity_normed = max(steering_velocity_normed, -1)
        # elif steering_velocity_normed > 0:
        #     steering_velocity_normed = min(steering_velocity_normed, 1)
        # acceleration_normed = 0
        # print(steering_velocity_normed)
        # return [[acceleration_normed, steering_velocity_normed]], None