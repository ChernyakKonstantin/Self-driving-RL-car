from .car_config import car_config
from .sensor_config import sensor_config
from .road_config import road_config

config = {
    "render": True,
    "window_size": (200, 400),
    "intermediate_reward": 1,
    "loose_reward": -5,
    **car_config,
    **sensor_config,
    **road_config
}

