from environments import TrainToSteerEnv, GodotClient
from stable_baselines3 import PPO
from stable_baselines3.common.env_util import make_vec_env
from functools import partial

ADDRESS = "localhost"
PORT = 9090
CHUNK_SIZE = 4096

def train_to_steer_on_parking_sensors():
    env_fn = partial(TrainToSteerEnv, engine_client=GodotClient(engine_address=(ADDRESS, PORT), chunk_size=CHUNK_SIZE))
    env = make_vec_env(env_fn, n_envs=1)
    model = PPO(
        "MultiInputPolicy",
        env,
        verbose=1,
        device="cpu",
        tensorboard_log="/home/cherniak/Self-driving-RL-car/logs/train_to_steer_on_parking_sensors",
        learning_rate=3 * 1e-3,
    )
    model.learn(total_timesteps=25000)