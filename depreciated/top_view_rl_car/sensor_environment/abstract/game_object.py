from abc import ABCMeta, abstractmethod
from typing import Any


class GameObject(metaclass=ABCMeta):
    """
    A game object abstract class. It should implements "show" method.
    """

    @abstractmethod
    def show(self, surface: Any):
        raise NotImplementedError
