import os
from functools import partial

import numpy as np
import torch
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env

from environments import GodotClient, TrainToSteerEnv
from models.parking_sensor_network import ParkingSensorExtractor, ParkingSensorNetwork
from policies import CustomActorCriticPolicy

ADDRESS = "localhost"
PORT = 9091
CHUNK_SIZE = 4096
PRETRAINED_ENCODER_WEIGHTS_PATTH = "/home/cherniak/Self-driving-RL-car/logs/pretrain_parking_sensor_encoder_with_icm/lightning_logs/version_0/checkpoints/epoch=49-step=3350.ckpt"
LOG_DIR = "/home/cherniak/Self-driving-RL-car/logs/train_to_steer_on_parking_sensors/termination_on_collision"
LOG_NAME = "parking_sensors_net_pretrained_with_icm_encoder_PPO"
SUFFIX = "_1"
TOTAL_TIMESTEPS = 150000
N_STEPS = 4096
CHECKPOINT_FREQUENCY = 5200
LR = 1e-3

def train_to_steer_on_parking_sensors():
    env_fn = partial(
        TrainToSteerEnv,
        engine_client=GodotClient(engine_address=(ADDRESS, PORT), chunk_size=CHUNK_SIZE),
        terminate_on_crash=True,
        wheel_rotation_limit_per_step=(-1 / 15, 1/15),
    )
    env = make_vec_env(env_fn, n_envs=1)
    custom_network_builder = partial(ParkingSensorNetwork, pretrained_encoder_weights_path=PRETRAINED_ENCODER_WEIGHTS_PATTH)

    # TODO: try masacable ppo and disretized action to enable out-of-box masking

    policy_kwargs = {
        "custom_network_builder": custom_network_builder,
        "features_extractor_class": ParkingSensorExtractor,
    }

    model = PPO(
        CustomActorCriticPolicy,
        policy_kwargs=policy_kwargs,
        n_steps=N_STEPS,
        env=env,
        use_sde=False,
        learning_rate=LR,
        verbose=1,
        device="cpu",
        seed=0,
        tensorboard_log=LOG_DIR,
    )
    # model.set_parameters("/home/cherniak/Self-driving-RL-car/train_to_steer_on_parking_sensors_PPO_1.zip")
    model.learn(
        callback=CheckpointCallback(
            save_freq = CHECKPOINT_FREQUENCY,
            save_path = os.path.join(LOG_DIR, LOG_NAME + SUFFIX, "checkpoints"),
        ),
        total_timesteps=TOTAL_TIMESTEPS,
        tb_log_name=LOG_NAME,
        progress_bar=True,
    )
    model.save(os.path.join(LOG_DIR, LOG_NAME + SUFFIX, "checkpoints", "last.zip"))
