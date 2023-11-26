import numpy as np
from typing import Dict

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

        self.tgt_x: float
        self.tgt_y: float

        self.reset()

    def position_is_matched(self, x, y) -> bool:
        x_cond =  (self.tgt_x - self.catch_radius) <= x <= (self.tgt_x + self.catch_radius)
        y_cond =  (self.tgt_y - self.catch_radius) <= y <= (self.tgt_y + self.catch_radius)
        return x_cond and y_cond

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