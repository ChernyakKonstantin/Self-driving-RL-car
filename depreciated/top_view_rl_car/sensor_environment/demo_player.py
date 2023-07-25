from .environment import SensorEnvironment
from .congifurations import config

class DemoPlayer:
    def __init__(self):
        self._env = SensorEnvironment(config)

    def play(self):
        self._env.reset()
        while True:
            if self._env.is_closed():
                break
            action = self._env.action_space.sample()
            _, _, is_done, _ = self._env.step(action)
            self._env.render()
            if is_done:
                self._env.reset()


