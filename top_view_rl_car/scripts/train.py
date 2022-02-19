from stable_baselines3 import PPO

from top_view_rl_car.sensor_environment import SensorEnvironment
from top_view_rl_car.sensor_environment import config

# Create environment
env = SensorEnvironment(config)
# Instantiate the agent
model = PPO('MultiInputPolicy', env, verbose=1, device="cuda")
# Train the agent
model.learn(total_timesteps=int(1e5))
