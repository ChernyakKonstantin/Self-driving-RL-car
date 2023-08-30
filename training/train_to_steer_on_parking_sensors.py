import os
from functools import partial
from . import protobuf_message_module
from stable_baselines3 import PPO
from stable_baselines3.common.callbacks import CheckpointCallback
from stable_baselines3.common.env_util import make_vec_env

from environments import TrainToSteerEnv
from models.parking_sensor_network import ParkingSensorExtractor, ParkingSensorNetwork
from policies import CustomActorCriticPolicy

ADDRESS = "localhost"
PORT = 9091
CHUNK_SIZE = 4096
TERMINATE_ON_CRASH = True

PRETRAINED_ENCODER_WEIGHTS_PATH = None # "/home/cherniak/Self-driving-RL-car/logs/pretrain_parking_sensor_encoder_with_icm/lightning_logs/version_0/checkpoints/epoch=49-step=3350.ckpt"
FREEZE_ENCODER = True

LOG_DIR = "/home/cherniak/Self-driving-RL-car/logs/train_to_steer_on_parking_sensors/termination_on_collision"
LOG_NAME = "parking_sensors_net_pretrained_with_icm_frozen_encoder_PPO"
SUFFIX = "_2"

TOTAL_TIMESTEPS = 150000
N_STEPS = 4096
CHECKPOINT_FREQUENCY = 5200
LR = 1e-3

def train_to_steer_on_parking_sensors():
    env_fn = partial(
        TrainToSteerEnv,
        protobuf_message_module,
        engine_address=(ADDRESS, PORT),
        engine_chunk_size=CHUNK_SIZE,
        terminate_on_crash=TERMINATE_ON_CRASH,
        wheel_rotation_limit_per_step=(-1 / 15, 1/15),
    )
    env = make_vec_env(env_fn, n_envs=1, seed=0)
    custom_network_builder = partial(
        ParkingSensorNetwork,
        pretrained_encoder_weights_path=PRETRAINED_ENCODER_WEIGHTS_PATH,
        freeze_encoder=FREEZE_ENCODER,
    )

    # TODO: try maskable ppo and disretized action to enable out-of-box masking

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
    # model.set_parameters("/home/cherniak/Self-driving-RL-car/logs/train_to_steer_on_parking_sensors/termination_on_collision/parking_sensors_net_pretrained_with_icm_frozen_encoder_PPO_1/checkpoints/rl_model_26000_steps.zip")
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
