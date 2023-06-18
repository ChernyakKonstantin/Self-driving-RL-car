import json
import socket
from typing import Any, Dict, Tuple
import numpy as np

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

    # TODO: implement timeout and return False if timeout is exceeded.
    # TODO: data type should be infered from response
    def request(self, request: Dict[str, Any], response_dtype: str) -> Dict[str, Any]:
        request_bytes = json.dumps(request).encode("utf-8")
        with socket.create_connection(self.engine_address) as sock:
            sock.sendall(request_bytes)
            chunks = b''
            while True:
                chunk = sock.recv(self.chunk_size)
                if not chunk:
                    break
                chunks += chunk
        if len(chunks) == 0:
            response = None
        else:
            if response_dtype == "int32":
                response = np.frombuffer(chunks, dtype=np.int32)
            elif response_dtype == "float32":
                response = np.frombuffer(chunks, dtype=np.float32)
            elif response_dtype == "dictionary":
                response = json.loads(chunks.decode("utf-8"))
            elif response_dtype == "image_dictionary":
                response = {}
                print(len(chunks))
                while len(chunks) > 0:
                    key_len = np.frombuffer(chunks[:4], dtype=np.uint32)[0]
                    chunks = chunks[4:]
                    key = chunks[:key_len].decode()
                    chunks = chunks[key_len:]
                    data_len = np.frombuffer(chunks[:4], dtype=np.uint32)[0]
                    chunks = chunks[4:]
                    data = np.frombuffer(chunks[:data_len], dtype=np.uint8)
                    data = data.reshape(240,360,3)
                    chunks = chunks[data_len:]
                    response[key] = data
                    print(len(chunks))
                # key_length = chunks[:4]
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
            requested_observation: Tuple[Tuple[int, str]],
        ) -> Dict[str, Any]:
        """
        Request engine to perform given action and return specified observations.
        """
        print(f"Action response: {self.request({self.ACTION_KEY: action}, 'int32')}\n")
        response = {}
        for (observation_key, observation_dtype) in requested_observation:
            print(observation_key)
            request = {self.OBSERVATION_KEY: observation_key}
            response[observation_key] = self.request(request, observation_dtype)
            print(f"Result: {response[observation_key]}\n")
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
