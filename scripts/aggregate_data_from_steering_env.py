import sys

sys.path.append("..")

from tqdm import tqdm
import random
import json
import numpy as np
from copy import deepcopy
from environments import GodotClient, TrainToSteerEnv

STORAGE_PATH = "/home/cherniak/Self-driving-RL-car/steering_data.json"

ADDRESS = "localhost"
PORT = 9090
CHUNK_SIZE = 4096

client = GodotClient((ADDRESS, PORT), CHUNK_SIZE)
env = TrainToSteerEnv(client, terminate_on_crash=True)

def preprocess_observation(observation):
    observation["steering"] = observation["steering"].astype(np.float64)
    return observation

terminated = False
observation_after = None
storage = []
for i in tqdm(range(int(2 * 1e4))):
    record = {}

    if i == 0 or random.random() < 1e-3 or terminated:
       observation_before, _ = env.reset()
       observation_before = preprocess_observation(observation_before)
       record["reset"] = True
    else:
        assert observation_after is not None
        observation_before = deepcopy(observation_after)
        record["reset"] = False

    action = np.random.uniform(-1/15, 1/15, 1)

    observation_after, _, terminated, _, _ = env.step(action)
    observation_after = preprocess_observation(observation_after)

    record["observation_before"] = observation_before
    record["observation_after"] = observation_after
    record["action"] = action.astype(np.float64).item()
    record["terminated"] = bool(terminated)

    storage.append(record)

with open(STORAGE_PATH, "w") as f:
    json.dump(storage, f, indent=4)