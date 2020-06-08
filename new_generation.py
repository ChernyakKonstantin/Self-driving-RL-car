from obstacle import Line
from environment import Environment
import random

X_SHIFT = 15
Y_SHIFT = 30
ROAD_WIDTH = 20

START_X = Environment.INIT_X - ROAD_WIDTH / 2
START_Y = 0

def generate_world():
    first_point = (START_X, START_Y)
    while first_point[1] < Environment.WORLD_LENGTH:
        second_point_x = first_point[0] + random.choice([-1,1]) * random.randint(0, X_SHIFT)
        second_point_y = first_point[1] + random.choice([-1,1]) * random.randint(0, Y_SHIFT)
        second_point = (second_point_x, second_point_y)
        Line(first_point, second_point)
        first_point = second_point



