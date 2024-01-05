from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from pursuit import PursuitEnv
from stable_baselines3.common.callbacks import CheckpointCallback
import os

LOAD_PATH = r"C:\Users\cherniak\pet_projects\Self-driving-RL-car\logs\train_to_reach target\default_SB_3\checkpoints\rl_model_382464000_steps.zip"

if __name__ == "__main__":
    env = make_vec_env(lambda: PursuitEnv(render=True), n_envs=1, seed=0)
    model = PPO.load(LOAD_PATH, env=env, device="cpu")
    vec_env = model.get_env()
    obs = vec_env.reset()
    while True:
        action, _states = model.predict(obs, deterministic=True)
        print(action)
        obs, rewards, dones, info = vec_env.step(action)
        if dones[0]:
            obs = vec_env.reset()
            print()
            print()
            print()
