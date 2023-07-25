from abc import ABCMeta, abstractmethod


class Observer(metaclass=ABCMeta):
    """
    Observer abstract class.
    """

    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError
