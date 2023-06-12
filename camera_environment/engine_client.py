import json
import socket
from typing import Any, Dict, Tuple


class EngineClient:
    STATUS_KEY = "status"
    CONFIG_KEY = "config"
    RESET_KEY = "reset"
    ACTION_KEY = "action"
    OBSERVATION_KEY = "observation"

    TIMEOUT_EXCEEDED = -1

    def __init__(
        self,
        engine_address: Tuple[str, int],
        chucnk_size: int = 4096
    ) -> None:
        """
        Simulator engine client class.
        It requests for current state and send the RL-agent action.
        engine_address: tuple of (`IP-address`, `port`).
        chucnk_size: int: size of the chunk to receive response from engine.
        """
        self.engine_address = engine_address
        self.chucnk_size = chucnk_size

    # TODO: implement timeout and return False if timeout is exceeded.
    def request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        request_bytes = json.dumps(request).encode("utf-8")
        with socket.create_connection(self.engine_address) as sock:
            sock.sendall(request_bytes)
            chunks = b''
            while True:
                chunk = sock.recv(self.chucnk_size)
                if not chunk:
                    break
                chunks += chunk
        response = json.loads(chunks.decode("utf-8"))
        return response

    # # TODO subject of changes
    # def request_is_ready(self) -> bool:
    #     """
    #     Request engine if it is ready to start.
    #     """
    #     request = {self.STATUS_KEY: 1}
    #     return self.request(request)

    # # TODO subject of changes
    # def configure(self, config: Dict[str, Any]) -> bool:
    #     """
    #     Configure the engine.
    #     """
    #     request = {self.CONFIG_KEY: config}
    #     return self.request(request)

    def request_step(
            self,
            action: Dict[str, Any],
            requested_observation: Tuple[int],
        ) -> Dict[str, Any]:
        """
        Request engine to perform given action and return specified observations.
        """
        request = {
            self.ACTION_KEY: action,
            self.OBSERVATION_KEY: requested_observation,
        }
        return self.request(request)

    # def reset(
    #         self,
    #         requested_observation: Tuple[int],
    #     ) -> Dict[str, Any]:
    #     """
    #     Request engine to reset environment and return specified observations.
    #     """
    #     request = {
    #         self.RESET_KEY: 1,  # TODO: subject of changes
    #         self.OBSERVATION_KEY: requested_observation,
    #     }
    #     return self.request(request)
