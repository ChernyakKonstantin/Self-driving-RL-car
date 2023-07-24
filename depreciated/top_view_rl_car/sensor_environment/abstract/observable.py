from abc import ABCMeta, abstractmethod
from .observer import Observer

class Observable(metaclass=ABCMeta):
    """
    Observable abstract class.
    """

    def __init__(self):
        self._observers = []

    @abstractmethod
    def _notify(self):
        raise NotImplementedError

    def attach(self, observer: Observer):
        self._observers.append(observer)

    def detach(self, observer: Observer):
        self._observers.remove(observer)
