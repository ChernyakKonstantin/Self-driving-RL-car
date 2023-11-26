from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from pursuit import PursuitEnv
from stable_baselines3.common.callbacks import CheckpointCallback
import os

LOG_DIR = "/Users/cherniak/pet_projects/Self-driving-RL-car/logs/train_to_reach target"
LOG_NAME = "default_SB"
SUFFIX = "_1"

DEVICE = "cpu"

N_ENVS = 256
TOTAL_TIMESTEPS = int(3 * 1e9)
N_STEPS = int(1.8 * 1e4)
CHECKPOINT_FREQUENCY = int(1.8 * 1e4)

if __name__ == "__main__":
    env = make_vec_env(lambda: PursuitEnv(), n_envs=N_ENVS, seed=0)
    model = PPO("MultiInputPolicy", env=env, n_steps=N_STEPS, tensorboard_log=LOG_DIR, device=DEVICE, verbose=1)
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