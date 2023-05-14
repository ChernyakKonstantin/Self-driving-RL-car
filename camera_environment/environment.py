import sys
from typing import Any, List, Tuple, Union, Dict

import gym
import numpy as np
import pygame

from .car import Car
from .collision_detector import CollisionDetector
from .sensor_viewer import SensorViewer
from .sterring_wheel_viewer import SteeringWheelViewer
from .world import World


class SensorEnvironment(gym.Env):