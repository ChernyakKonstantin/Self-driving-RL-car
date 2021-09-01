from .environment import Environment


class DemoPlayer:
    def __init__(self):
        self._env = Environment()

    def play(self):
        self._env.reset()
        while True:
            if self._env.is_closed():
                break
            action = tuple([e.item() for e in self._env.action_space.sample().values()])
            _ = self._env.step(action)
            self._env.render()


