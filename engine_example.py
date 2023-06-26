from camera_environment.engine_client import EngineClient
from camera_environment.enums import Request
from random import choice
import cv2

ADDRESS = "localhost"
PORT = 9090

client = EngineClient((ADDRESS, PORT), chunk_size=4096)

c = 0
while True:
    c += 1
    action = {
        "steering_delta": choice([-1,1]),
        "acceleration_delta": 1, #choice([-1,1]),
    }

    requested_observation = [
        Request.FRAME,
        Request.IS_CRASHED,
        Request.WHEEL_POSITION,
        Request.OBSTACLE_PROXEMITY,
        Request.SPEED,
    ]

    response = client.request_step(action, requested_observation)

    for name in response["cameras"].keys():
        print
        cv2.imshow(name, response["cameras"][name][0])
    if cv2.waitKey(25) & 0xFF == ord('q'):
        break
    print(c)
cv2.destroyAllWindows()