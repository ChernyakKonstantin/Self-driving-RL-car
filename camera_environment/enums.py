# TODO: probably move out to json-file to share between Python and Godot.

from enum import IntEnum


class Response(IntEnum):
    FAIL = 0
    SUCCESS = 1


class Request(IntEnum):
    """Int8."""
    FRAME = 1
    IS_CRASHED = 2
    WHEEL_POSITION = 3
    SPEED = 4
    OBSTACLE_PROXEMITY = 5

class DataType(IntEnum):
    INT32 = 1
    FLOAT32 = 2
    JSON = 3
    NAMED_IMAGE = 4