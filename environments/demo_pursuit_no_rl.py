from stable_baselines3.common.env_util import make_vec_env
from pursuit import PursuitEnv
from determenistic_controller import DeterministicController
import time
if __name__ == "__main__":
    vec_env = make_vec_env(lambda: PursuitEnv(render=True), n_envs=1, seed=0)
    model = DeterministicController(vec_env.envs[0].env.car)
    obs = vec_env.reset()
    vec_env.envs[0].env.car.velocity = 1
    vec_env.envs[0].env.car.acceleration = 0
    vec_env.envs[0].env.car.steering = 0.0
    vec_env.envs[0].env.car.orientation = -3.14 / 2
    vec_env.envs[0].env.world.tgt_x = 80
    vec_env.envs[0].env.world.tgt_y = 20
    obs, rewards, dones, info = vec_env.step([[0,0]])

    while True:
        steering = model.predict(obs)
        print(steering)
        obs, rewards, dones, info = vec_env.step([[0, steering]])
        time.sleep(0.1)
        if dones[0]:
            break
            # obs = vec_env.reset()
            # print()
            # print()
            # print()

