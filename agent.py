import collections
from typing import Tuple, Union
import tensorflow as tf
import numpy as np

Experience = collections.namedtuple(typename='Experience',
                                    field_names=[
                                        'state',
                                        'action',
                                        'reward',
                                        'done',
                                        'new_state',
                                    ])


class Agent:
    def __init__(self, environment, net):
        self._environment = environment
        self._net = net
        self._state = None
        self._total_reward = None
        self._reset()

    def _reset(self) -> None:
        self._state = self._environment.reset()
        self._total_reward = 0.0

    def _predict_action(self) -> int:
        q_vals = self._net(np.expand_dims(self._state, axis=0))
        action = tf.argmax(q_vals, axis=1).numpy().item()
        return action

    def _get_action(self, epsilon: float) -> int:
        if np.random.random() < epsilon:
            return self._environment.sample_action()
        else:
            return self._predict_action()

    def training_step(self, epsilon: float) -> Tuple[Union[None, float], Experience]:
        done_reward = None
        action = self._get_action(epsilon)
        action_list = self._environment.get_action_list(action)
        new_state, reward, is_done, _ = self._environment.step(action_list)
        self._total_reward += reward
        experience = Experience(self._state, action, reward, is_done, new_state)
        self._state = new_state
        if is_done:
            done_reward = self._total_reward
            self._reset()
        return done_reward, experience

    def inference_step(self) -> Union[None, float]:
        done_reward = None
        action = self._predict_action()
        action_list = self._environment.get_action_list(action)
        new_state, reward, is_done, _ = self._environment.step(action_list)
        self._total_reward += reward
        self._state = new_state
        if is_done:
            done_reward = self._total_reward
            self._reset()
        return done_reward
