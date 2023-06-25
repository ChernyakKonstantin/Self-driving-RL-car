from camera_environment.engine_client import EngineClient
from camera_environment.enums import Request
from random import choice
ADDRESS = "localhost"
PORT = 9090

client = EngineClient((ADDRESS, PORT), chunk_size=4096)


while True:
    action = {
        "steering_delta": choice([-1,1]),
        "acceleration_delta": 1, #choice([-1,1]),
    }

    requested_observation = [
        Request.FRAME,
        # Request.IS_CRASHED,
        # Request.WHEEL_POSITION,
        # Request.OBSTACLE_PROXEMITY,
        # Request.SPEED,
    ]

    response = client.request_step(action, requested_observation)
    print(response)
