import math

from .abstract_classes import GameObject, Observable, Resetable
from .sensor import Sensor


class Car(Observable, GameObject, Resetable):
    WIDTH = 10  # Ширина автомобиля в см, 1см = 1px
    LENGTH = 20  # Длина автомобиля в см, 1см = 1px
    RADIUS = 15  # Радиус поворота автомобиля, см
    INIT_ORIENTATION = 0  # Градусы. Автомобиль перпендикулярен оси X
    MAX_SPEED = 0.3

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __init__(self, x, y):
        super().__init__()
        self._init_x = x
        self._init_y = y
        self._x = self._init_x
        self._y = self._init_y
        self._orientation = math.radians(Car.INIT_ORIENTATION)
        self._velocity = 0

        self.sensor = Sensor(self._x, self._y, self._orientation)
        self.attach(self.sensor)

    def _notify(self):
        for observer in self._observers:
            observer.update(self._x, self._y, self._orientation)

    def move(self, steering_angle: float, velocity: float) -> None:
        self._update_velocity(velocity)
        self._steer(steering_angle)
        self._move_forward()
        self._notify()

    # TODO: update
    def _validate_velocity(self, velocity: float) -> float:
        if velocity > Car.MAX_SPEED:
            return Car.MAX_SPEED
        elif velocity < 0:
            # В текущей реализации автомобиль не может двигаться в обратном направлении
            return 0
        else:
            return velocity

    def _update_velocity(self, velocity: float) -> None:
        self._velocity = self._validate_velocity(velocity)

    def _move_forward(self) -> None:
        # Автомобиль движется сверху вниз
        self._y += self._velocity * math.cos(self._orientation)
        self._x += self._velocity * math.sin(self._orientation)

    def _steer(self, cur_angle: float) -> None:
        self._orientation = math.radians(cur_angle)

    def reset(self):
        self._x = self._init_x
        self._y = self._init_y
        self._orientation = math.radians(Car.INIT_ORIENTATION)
        self._velocity = 0
        self._notify()


    def show(self, surface) -> None:
        raise NotImplementedError
