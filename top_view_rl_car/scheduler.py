class EpsilonScheduler:
    def __init__(self, n_steps: int, start_value: float = 1.0, end_value: float = 0.05):
        self._start_value = start_value
        self._end_value = end_value
        self._frame_index = 0
        self._n_steps = n_steps
        self._step = (self._start_value - self._end_value) / self._n_steps

    def get_epsilon(self):
        if self._frame_index <= self._n_steps:
            epsilon = self._start_value - self._step
        else:
            epsilon = self._end_value
        self._frame_index += 1
        return epsilon
