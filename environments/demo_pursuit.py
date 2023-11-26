from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from pursuit import PursuitEnv
from stable_baselines3.common.callbacks import CheckpointCallback
import os

LOAD_PATH = "/Users/cherniak/pet_projects/Self-driving-RL-car/logs/train_to_reach target/default_SB_1/checkpoints/rl_model_193536000_steps.zip"

if __name__ == "__main__":
    env = make_vec_env(lambda: PursuitEnv(), n_envs=1, seed=0)
    model = PPO.load(LOAD_PATH, env=env)
    vec_env = model.get_env()
    obs = vec_env.reset()
    while True:
        action, _states = model.predict(obs, deterministic=True)
        obs, rewards, dones, info = vec_env.step(action)
        if dones[0]:
            obs = vec_env.reset()
   