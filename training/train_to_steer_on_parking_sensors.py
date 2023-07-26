from functools import partial

import numpy as np
from stable_baselines3 import TD3, PPO
from stable_baselines3.common.env_util import make_vec_env
from stable_baselines3.common.noise import NormalActionNoise, VectorizedActionNoise
import torch

from environments import GodotClient, TrainToSteerEnv

ADDRESS = "localhost"
PORT = 9090
CHUNK_SIZE = 4096

def train_to_steer_on_parking_sensors():
    env_fn = partial(TrainToSteerEnv, engine_client=GodotClient(engine_address=(ADDRESS, PORT), chunk_size=CHUNK_SIZE))
    env = make_vec_env(env_fn, n_envs=1)
    # action_noise = VectorizedActionNoise(NormalActionNoise(mean=np.array([0., ]), sigma=np.array([1, ])), n_envs=1)
    # model = TD3(
    #     "MultiInputPolicy",
    #     env,
    #     learning_rate=1e-3,
    #     learning_starts=2000,
    #     action_noise=action_noise,
    #     verbose=1,
    #     device="cpu",
    #     seed=0,
    #     tensorboard_log="/home/cherniak/Self-driving-RL-car/logs/train_to_steer_on_parking_sensors",
    # )
    # TODO: try masacable ppo and disretized action to enable out-of-box masking

    policy_kwargs = {
        "activation_fn": torch.nn.ReLU,
        "net_arch": [64,64],
    }

    model = PPO(
        "MultiInputPolicy",
        policy_kwargs=policy_kwargs,
        env=env,
        use_sde=False,
        learning_rate=1e-3,
        verbose=1,
        device="cpu",
        seed=0,
        tensorboard_log="/home/cherniak/Self-driving-RL-car/logs/train_to_steer_on_parking_sensors",
    )
    # model.set_parameters("/home/cherniak/Self-driving-RL-car/train_to_steer_on_parking_sensors_PPO_1.zip")
    model.learn(total_timesteps=150000)
    # model.save("/home/cherniak/Self-driving-RL-car/train_to_steer_on_parking_sensors_TD3_1.zip")
    model.save("/home/cherniak/Self-driving-RL-car/train_to_steer_on_parking_sensors_PPO_1.zip")