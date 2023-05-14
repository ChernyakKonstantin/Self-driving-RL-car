from enum import IntEnum


class Response(IntEnum):
    FAIL = 0
    SUCCESS = 1


class Request(IntEnum):
    """Int8."""
    FRAME = 1
    IS_CRASHED = 2
    WHEEL_POSITION = 3
    ACCELERATION = 4
    SPEED = 5
    DISTANCE_TO_OBSTACLE = 6
    # TODO: subject of further changes. Currently its assumed to be position in the graph.
    NAVIGATION = 7
