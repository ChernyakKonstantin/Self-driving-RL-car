from typing import Dict, Any, Tuple
import numpy as np

from .enums import Request, Response


class EngineClient:
    def __init__(
        self,
        address: Tuple[str, int],
    ) -> None:
        """
        Simulator engine client base class.
        It requests for current state and send the RL-agent action.
        adress: tuple of (`IP-address`, `port`).
        """

    def request_frame() -> np.ndarray:
        raise NotImplementedError

    def request_is_crashed() -> bool:
        raise NotImplementedError

    def request_wheel_position() -> float:
        raise NotImplementedError

    def send_action(action: Dict[str, Any]):
        raise NotImplementedError

    def reset(self) -> Dict[str, Any]:
        raise NotImplementedError
