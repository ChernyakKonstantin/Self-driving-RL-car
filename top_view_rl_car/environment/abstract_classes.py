from abc import ABCMeta, abstractmethod
from typing import Any, Union


class GameObject(metaclass=ABCMeta):
    """
    Абстрактный класс объекта игры.
    Каждый объект игры должен иметь метод отрисовки.
    """

    @abstractmethod
    def show(self, surface: Any):
        """Метод отрисовки объекта."""


class Observer(metaclass=ABCMeta):
    """
    Абстрактный класс объекта наблюдателя.
    """

    @abstractmethod
    def update(self, *args, **kwargs):
        raise NotImplementedError


class Observable(metaclass=ABCMeta):
    """
    Абстрактный класс объекта издателя.
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

class Resetable(metaclass=ABCMeta):
    """
    Абстрактный класс сбрасываемого объекта.
    """

    @abstractmethod
    def reset(self):
        raise NotImplementedError