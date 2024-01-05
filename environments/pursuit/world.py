import numpy as np
from typing import Dict
from scipy import spatial

class World:
    def __init__(self, width=100, height=100, tgt_spawn_zone_ratio: float=0.8, catch_radius=1, seed=0):
        np.random.seed(seed)

        self.width = width
        self.height = height
        self.catch_radius = catch_radius  # m

        self.left_spawn_limit = self.width * (1 - tgt_spawn_zone_ratio) / 2
        self.right_spawn_limit = self.width * (1 + tgt_spawn_zone_ratio) / 2
        self.top_spawn_limit = self.height * (1 - tgt_spawn_zone_ratio) / 2
        self.bottom_spawn_limit = self.height * (1 + tgt_spawn_zone_ratio) / 2
        self.max_distance_to_target = spatial.distance.euclidean((0, 0), (self.width, self.height))
        self.tgt_x: float
        self.tgt_y: float

        self.reset()

    def get_distance_to_target(self, x, y) -> float:
        return spatial.distance.euclidean((x, y), (self.tgt_x, self.tgt_y))

    def is_target_reached(self, x, y) -> bool:
        get_distance_to_target = self.get_distance_to_target(x, y)
        return get_distance_to_target <= self.catch_radius

    def sample_tgt_position(self):
        self.tgt_x = np.random.rand() * np.random.choice([self.left_spawn_limit, self.right_spawn_limit])
        self.tgt_y = np.random.rand() * np.random.choice([self.top_spawn_limit, self.bottom_spawn_limit])

    def reset(self):
        self.sample_tgt_position()

    def get_state(self) -> Dict[str, float]:
        state = {
            "tgt_x": [self.tgt_x,],
            "tgt_y": [self.tgt_y,],
        }
        return state

    def maybe_handle_collison(self, actor) -> bool:
        collision = False
        if actor.x > self.width:
            actor.x = self.width
            collision=True
        elif actor.x < 0:
            actor.x = 0
            collision=True
        if actor.y > self.height:
            actor.y = self.height
            collision=True
        elif actor.y < 0:
            actor.y = 0
            collision=True
        return collision
