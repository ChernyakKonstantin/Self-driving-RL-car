from environments.godot_client import GodotClient
from environments.godot_client.enums import Request
from random import choice
import cv2
import numpy as np

ADDRESS = "localhost"
PORT = 9090

client = GodotClient((ADDRESS, PORT), chunk_size=4096)

c = 0
while True:
    c += 1
    action = {
        "steering_delta": choice([-0.2, 0.2]),
        "engine_force_delta": 1, #choice([-1/50, 1/50]),
    }

    requested_observation = [
        # Request.FRAME,
        # Request.LIDAR,
        Request.IS_CRASHED,
        # Request.WHEEL_POSITION,
        # Request.PARKING_SENSORS,
        # Request.SPEED,
    ]

    response = client.request_step(action, requested_observation)
    print(c)

    if "lidar" in response:
        horizontal_fov = 120
        vertical_fov = 60
        horizontal_resolution = 1
        vertical_resolution = 1
        max_dist = 100
        SCALING = 5

        height = int(vertical_fov/ vertical_resolution)
        width = int(horizontal_fov/ horizontal_resolution)
        image = np.zeros((height, width), dtype=np.uint8)
        for e in response["lidar"][-1]:
            x, y, dist = e
            x += horizontal_fov / 2
            y += vertical_fov / 2
            x *= 1 / horizontal_resolution
            y *= 1 / vertical_resolution
            image[int(y), int(x)] = 255 - int(np.log(dist) / np.log(max_dist) * 255)
        image = np.flip(image, axis=1)
        image = cv2.resize(image, (int(width * horizontal_resolution * SCALING), int(round(height * vertical_resolution * SCALING ))))
        cv2.imshow("lidar", image)

    if "cameras" in response:
        for name in response["cameras"].keys():
            print
            cv2.imshow(name, cv2.cvtColor(response["cameras"][name][0], cv2.COLOR_RGB2BGR))

    if "lidar" in response or "cameras" in response:
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()