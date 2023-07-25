from stable_baselines3 import PPO

from top_view_rl_car.sensor_environment import Environment
from stable_baselines3.common.logger import configure


env = Environment()
# We recommend using a `batch_size` that is a factor of `n_steps * n_envs`.
model = PPO(policy='MlpPolicy',
            env=env,
            verbose=1)
model.learn(total_timesteps=1000)
model.save(model_path)

obs = env.reset()
for i in range(1000):
    action, _states = model.predict(obs, deterministic=True)
    obs, rewards, dones, info = env.step(action)
    if dones:
        obs = env.reset()
