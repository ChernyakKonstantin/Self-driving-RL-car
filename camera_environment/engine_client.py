import json
import socket
from typing import Any, Dict, Tuple
import numpy as np
from collections import defaultdict
from .enums import DataType

class EngineClient:
    STATUS_KEY = "status"
    CONFIG_KEY = "config"
    RESET_KEY = "reset"
    ACTION_KEY = "action"
    OBSERVATION_KEY = "observation"

    IMAGE_DIMS = (240, 360, 3)

    TIMEOUT_EXCEEDED = -1

    def __init__(
        self,
        engine_address: Tuple[str, int],
        chunk_size: int = 4096
    ) -> None:
        """
        Simulator engine client class.
        It requests for current state and send the RL-agent action.
        engine_address: tuple of (`IP-address`, `port`).
        chunk_size: int: size of the chunk to receive response from engine.
        """
        self.engine_address = engine_address
        self.chunk_size = chunk_size


    def _get_int32(self, data: bytes) -> Tuple[bytes, int]:
        raw_value = data[:4]
        value = np.frombuffer(raw_value, dtype=np.int32)[0]
        return data[4:], value

    def _get_float32(self, data: bytes) -> Tuple[bytes, float]:
        raw_value = data[:4]
        value = np.frombuffer(raw_value, dtype=np.float32)[0]
        return data[4:], value

    def _get_json(self, data: bytes) -> Tuple[bytes, Dict[str, Any]]:
        data, buffer_size = self._get_int32(data)
        raw_value = data[:buffer_size]
        value = json.loads(raw_value.decode("utf-8"))
        return data[buffer_size:], value

    def _get_string(self, data: bytes) -> Tuple[bytes, str]:
        data, buffer_size = self._get_int32(data)
        raw_value = data[:buffer_size]
        value = raw_value.decode()
        return data[buffer_size:], value

    def _get_named_images(self, data: bytes):
        values = defaultdict(list)

        data, number_of_keys = self._get_int32(data)
        for _ in range(number_of_keys):
            data, key = self._get_string(data)
            data, number_of_images = self._get_int32(data)
            for _ in range(number_of_images):
                data, buffer_size = self._get_int32(data)
                raw_value = data[:buffer_size]
                value = np.frombuffer(raw_value, dtype=np.uint8)
                value = value.reshape(self.IMAGE_DIMS)
                values[key].append(value)
                data = data[buffer_size:]
        return data, values

    def _get_data_from_stream(self, connection: socket.socket) -> bytes:
        chunks = b''
        while True:
            chunk = connection.recv(self.chunk_size)
            if not chunk:
                break
            chunks += chunk
        return chunks

    def _get_response(self, connection: socket.socket) -> Dict[str, Any]:
        data = self._get_data_from_stream(connection)
        response = {}
        data, elements_in_message = self._get_int32(data)
        for _ in range(elements_in_message):
            data, key = self._get_string(data)
            data, data_type = self._get_int32(data)
            if data_type == DataType.INT32:
                data, response[key] = self._get_int32(data)
            elif data_type == DataType.FLOAT32:
                data, response[key] = self._get_float32(data)
            elif data_type == DataType.JSON:
                data, response[key] = self._get_json(data)
            elif data_type == DataType.NAMED_IMAGE:
                data, response[key] = self._get_named_images(data)
            else:
                raise ValueError(f"Unknown data type: {data_type}")
        return response

    # TODO: implement timeout and return False if timeout is exceeded.
    def request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        request_bytes = json.dumps(request).encode("utf-8")
        with socket.create_connection(self.engine_address) as connection:
            connection.sendall(request_bytes)
            response = self._get_response(connection)
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
        response = self.request(request)
        return response

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
