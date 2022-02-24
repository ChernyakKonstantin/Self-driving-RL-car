from gym.wrappers import FrameStack, FlattenObservation
from stable_baselines3 import PPO

from top_view_rl_car.sensor_environment import SensorEnvironment
from top_view_rl_car.sensor_environment import config

# Create environment
env = SensorEnvironment(config)
env = FlattenObservation(env)
env = FrameStack(env, 4)
env = FlattenObservation(env)
# Instantiate the agent
model = PPO('MlpPolicy', env, verbose=1, device="cuda")
# Train the agent
model.learn(total_timesteps=int(1e5))
