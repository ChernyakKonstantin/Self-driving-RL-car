from abc import ABCMeta, abstractmethod


class Resetable(metaclass=ABCMeta):
    """
    Resetable object abstract class.
    """

    @abstractmethod
    def reset(self, *args, **kwargs):
        raise NotImplementedError
