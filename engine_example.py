from environments.godot_client import GodotClient
from environments.godot_client.enums import Request
from random import choice
import cv2
import numpy as np
import time
import matplotlib.pyplot as plt
import io
from mpl_toolkits import mplot3d

from typing import Dict, List, Any

ADDRESS = "localhost"
PORT = 9090

config = {
    "agent": {
        "lidar": {
            "horizontal_resolution": 1,
            "vertical_resolution": 1,
            "horizontal_fov": 360,
            "vertical_fov": 15,
            "ray_max_len": 1000,
            "return_distances": False,
        },
        "car": {
            "max_steering_angle": 0.2,
            "max_engine_force": 100,
        }
    },
    "environment": {
        "repeat_action": 8,
    }
}



def naive_steering_control(observation: Dict) -> float:
    steering = observation["steering"]
    parking_sensor = observation["parking_sensor"]

    left = min([
        parking_sensor["FrontLeft"][-1],
        # parking_sensor["Left"][-1],
        # parking_sensor["RearLeft"][-1],
    ])
    left = left / 2 # Normalize by dividing on maximum possible distance

    right = min([
        parking_sensor["FrontRight"][-1],
        # parking_sensor["Right"][-1],
        # parking_sensor["RearRight"][-1],
    ])
    right = right / 2 # Normalize by dividing on maximum possible distance

    right_steering = -1 * (1 - left)
    left_steering = 1 - right
    return (right_steering + left_steering) / 2

def draw_lidar_as_image(config, current_state):
    horizontal_fov = config["agent"]["lidar"]["horizontal_fov"]
    vertical_fov = config["agent"]["lidar"]["vertical_fov"]
    horizontal_resolution = config["agent"]["lidar"]["horizontal_resolution"]
    vertical_resolution = config["agent"]["lidar"]["vertical_resolution"]
    ray_max_len = config["agent"]["lidar"]["ray_max_len"]
    SCALING = 5

    height = int(vertical_fov/ vertical_resolution)
    width = int(horizontal_fov/ horizontal_resolution)
    image = np.zeros((height, width), dtype=np.uint8)
    for e in current_state["lidar"][-1]:
        x, y, dist = e
        x += horizontal_fov / 2
        y += vertical_fov / 2
        x *= 1 / horizontal_resolution
        y *= 1 / vertical_resolution
        image[int(y), int(x)] = 255 - int(dist / ray_max_len * 255)
    image = np.flip(image, axis=1)
    image = cv2.resize(image, (int(width * horizontal_resolution * SCALING), int(round(height * vertical_resolution * SCALING ))))
    cv2.imshow("lidar", image)

def draw_lidar_as_3d(current_state):
    x = []
    y = []
    z = []
    for e in current_state["lidar"][-1]:
        if len(e) > 0:
            x.append(e["x"])
            y.append(e["y"])
            z.append(e["z"])
    fig = plt.figure()
    ax = plt.axes(projection='3d')
    ax.scatter3D(x, z, y, s=1)
    ax.set_xlim(-10, 10)
    ax.set_ylim(-10, 10)
    ax.set_zlim(-2, 2)
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=180)
    buf.seek(0)
    img_arr = np.frombuffer(buf.getvalue(), dtype=np.uint8)
    buf.close()
    img = cv2.imdecode(img_arr, 1)
    cv2.imshow("1", img)

client = GodotClient((ADDRESS, PORT), chunk_size=4096)

while not client.check_if_server_is_ready():
    time.sleep(0.5)

client.configure(config)

c = 0
steering_delta = 0

while True:
    c += 1
    action = {
        "steering_delta": steering_delta,
        "engine_force_delta": 1, #choice([-1/50, 1/50]),
    }

    requested_observation = [
        # Request.CAMERA,
        Request.LIDAR,
        Request.IS_CRASHED,
        Request.WHEEL_POSITION,
        Request.PARKING_SENSORS,
        Request.SPEED,
        Request.GLOBAL_COORDINATES,
    ]

    current_state = client.request_step(action, requested_observation)
    print(c)

    steering_delta  = naive_steering_control(current_state)

    if "lidar" in current_state:
        if config["agent"]["lidar"]["return_distances"]:
            draw_lidar_as_image(config, current_state)
        else:
            draw_lidar_as_3d(current_state)

    if "camera" in current_state:
        for name in current_state["cameras"].keys():
            print
            cv2.imshow(name, cv2.cvtColor(current_state["cameras"][name][0], cv2.COLOR_RGB2BGR))

    if "lidar" in current_state or "cameras" in current_state:
        if cv2.waitKey(25) & 0xFF == ord('q'):
            break

cv2.destroyAllWindows()


