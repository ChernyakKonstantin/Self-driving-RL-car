from .abstract import Observer, Resetable


class ActionDetector(Observer, Resetable):
    """Класс предназначен для детекции изменения состояния объекта управления.
        Например, случай, когда автомобиль неподвижен и поворачивает колеса, классифицируется как статичное поведение,
        которое является нежелательным.
    """

    def __init__(self, limit: int = 10):
        """

        Args:
            limit (int): Число циклов программы, в рамках которого допустимо статичное поведение объекта управления.
        """
        self._limit = limit
        self._counter = 0
        self._prev_values = []

    def __call__(self) -> bool:
        self._counter += 1
        return self._check()

    def reset(self):
        self._counter = 0
        self._prev_values = []

    def update(self, *args):
        """args - любые величны, изменения которых отслеживаются."""
        no_updates = True
        if not self._prev_values:
            for arg in enumerate(args):
                self._prev_values.append(arg)
            no_updates = False
        else:
            for arg_id, arg in enumerate(args):
                if arg != self._prev_values[arg_id]:
                    no_updates = False
                    self._prev_values[arg_id] = arg
        if not no_updates:
            self._counter = 0

    def _check(self) -> bool:
        return self._counter >= self._limit
