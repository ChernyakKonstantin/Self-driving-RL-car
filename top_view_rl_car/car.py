import math

from .abstract_classes import GameObject, Observable
from .sensor import Sensor


class Car(Observable, GameObject):
    WIDTH = 10  # Ширина автомобиля в см, 1см = 1px
    LENGTH = 20  # Длина автомобиля в см, 1см = 1px
    RADIUS = 15  # Радиус поворота автомобиля, см
    ACCELERATION = 0.01
    INIT_ORIENTATION = 0  # Градусы. Автомобиль перпендикулярен оси X
    MAX_SPEED = 0.3
    BRAKE_FACTOR = 2
    RUBBER_FORCE_FACTOR = 0.1

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    def __init__(self, x, y):
        super().__init__()
        self._x = x
        self._y = y
        self._orientation = math.radians(Car.INIT_ORIENTATION)
        self._velocity = 0
        self._ang_velocity = 0

        self._actions = (
            self._accelerate,
            self._turn_left,
            self._turn_right,
            self._brake,
        )

        self.sensor = Sensor(self._x, self._y, self._orientation)

        self._attach(self.sensor)

    def _notify(self):
        for observer in self._observers:
            observer.update(self._x, self._y, self._orientation)

    def move(self, action_ids: list) -> None:
        for action_id in action_ids:
            self._actions[action_id]()
        self._rubbing_force()
        self._move_forward()
        self._notify()

    @staticmethod
    def _validate_velocity(velocity: float) -> float:
        if velocity > Car.MAX_SPEED:
            return Car.MAX_SPEED
        elif velocity < 0:
            # В текущей реализации автомобиль не может двигаться в обратном направлении
            return 0
        else:
            return velocity

    def _update_velocity(self, velocity: float) -> None:
        self._velocity = self._validate_velocity(velocity)
        self._ang_velocity = self._velocity / Car.RADIUS

    def _accelerate(self) -> None:
        velocity = self._velocity + Car.ACCELERATION
        self._update_velocity(velocity)

    def _brake(self) -> None:
        velocity = self._velocity - Car.BRAKE_FACTOR * Car.ACCELERATION
        self._update_velocity(velocity)

    def _rubbing_force(self) -> None:
        velocity = self._velocity - Car.RUBBER_FORCE_FACTOR * Car.ACCELERATION
        self._update_velocity(velocity)

    def _move_forward(self) -> None:
        # Автомобиль движется сверху вниз
        self._y += self._velocity * math.cos(self._orientation)
        self._x += self._velocity * math.sin(self._orientation)

    def _turn_left(self) -> None:
        rotation_angle = self._calc_angle()
        self._orientation += rotation_angle

    def _turn_right(self) -> None:
        rotation_angle = self._calc_angle()
        self._orientation -= rotation_angle

    def _calc_angle(self) -> float:
        arc_angle = self._ang_velocity  # Угол дуги, описываемой при повороте
        rotation_angle = arc_angle / 2  # Угол отклонения автомобиля при повороте
        return rotation_angle

    def show(self, surface) -> None:
        raise NotImplementedError
