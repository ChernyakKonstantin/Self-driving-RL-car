import os

import numpy as np
import tensorflow as tf
from tensorflow.keras.losses import MSE

from .agent import Agent
from .environment import Environment
from .experience_buffer import ExperienceBuffer
from .net import make_lstm_qdn
from .scheduler import EpsilonScheduler


class Training:
    # Параметры нейронной сети
    N_HIDDEN_UNITS = 16
    # Параметры обучения
    BELLMAN_GAMMA = 0.99
    MEAN_REWARD_BOUND = 500
    BATCH_SIZE = 4096
    LEARNING_RATE = 0.001
    REPLAY_START_SIZE = 10 ** 4
    TRAIN_PERIOD = 10 ** 4
    SYNC_TARGET_FRAMES = 3 * 10 ** 4
    EPOCHS = 10
    # Параметры накопления исторических данных
    REPLAY_SIZE = 10 ** 5
    # Параметры генератора случайного действия агента
    EPSILON_DECAY_LAST_FRAME = 2 * 10 ** 5
    EPSILON_START = 1.0
    EPSILON_FINAL = 0.02
    # Параметры среды обучения
    REPEATS_PER_STEP = 4

    @staticmethod
    def make_checkpoints_dir():
        if not os.path.exists('checkpoints'):
            os.mkdir('checkpoints')

    def __init__(self):
        self.make_checkpoints_dir()

        self._env = Environment(Training.REPEATS_PER_STEP)
        n_actions = len(self._env.actions)
        observation_shape = self._env.get_observation_shape()

        self._net = make_lstm_qdn(observation_shape, Training.REPEATS_PER_STEP, n_actions, Training.N_HIDDEN_UNITS)
        self._tgt_net = make_lstm_qdn(observation_shape, Training.REPEATS_PER_STEP, n_actions, Training.N_HIDDEN_UNITS)
        self._buffer = ExperienceBuffer(Training.REPLAY_SIZE)
        self._agent = Agent(self._env, self._net)
        self._scheduler = EpsilonScheduler(Training.EPSILON_DECAY_LAST_FRAME)

        self._total_rewards = []
        self._best_mean_reward = None
        self._frame_index = 0

    def _handle_reward(self, reward: float) -> None:
        self._total_rewards.append(reward)
        mean_reward = np.mean(self._total_rewards[-10:])
        if self._best_mean_reward is None or self._best_mean_reward < mean_reward:
            if self._best_mean_reward is not None:
                print("Best mean reward updated %.3f -> %.3f, model saved" % (self._best_mean_reward, mean_reward))
            self._best_mean_reward = mean_reward
            save_name = f'checkpoints/dqn_{self._best_mean_reward}/checkpoint'
            self._tgt_net.save_weights(save_name)

    def _is_solved(self) -> bool:
        if self._best_mean_reward:
            return self._best_mean_reward > Training.MEAN_REWARD_BOUND
        else:
            return False

    def _is_full_buffer(self) -> bool:
        return len(self._buffer) >= Training.REPLAY_START_SIZE

    def _is_to_sync_networks(self, frame_index: int) -> bool:
        return frame_index % Training.SYNC_TARGET_FRAMES == 0

    def _is_to_train_network(self, frame_index: int) -> bool:
        return frame_index % Training.TRAIN_PERIOD == 0

    def _sync_networks(self) -> None:
        self._tgt_net.set_weights(self._net.get_weights())
        print("Networks are synchronized")

    def _get_expected_state_action_values(self, rewards: np.ndarray, dones: np.ndarray,
                                          next_states: np.ndarray) -> np.ndarray:
        next_state_values = self._tgt_net.predict(next_states).max(axis=1)
        next_state_values[dones] = 0.0
        return next_state_values * Training.BELLMAN_GAMMA + rewards

    def _fit(self, batch: tuple) -> tf.Tensor:
        states, actions, rewards, dones, next_states = batch
        expected_state_action_values = self._get_expected_state_action_values(rewards, dones, next_states)

        with tf.GradientTape() as tape:
            q_val = self._net(states)
            idx = tf.stack([tf.range(actions.shape[0]), actions], axis=-1)
            state_action_values = tf.gather_nd(q_val, idx)
            loss = MSE(expected_state_action_values, state_action_values)

        # Backpropagation
        grads = tape.gradient(loss, self._net.trainable_variables)
        self._net.optimizer.apply_gradients(zip(grads, self._net.trainable_variables))
        return loss

    def train(self) -> list:
        done = False
        losses = []
        frame_index = 0

        while not done:
            if self._env.is_closed():
                done = True

            frame_index += 1
            if frame_index % 1000 == 0:
                print(frame_index)

            epsilon = self._scheduler.get_epsilon()
            reward, experience = self._agent.training_step(epsilon)
            self._buffer.append(experience)

            self._env.render()

            if not self._is_full_buffer():
                continue

            if reward is not None:
                self._handle_reward(reward)

            if self._is_solved():
                print(f'Solved in {frame_index} frames!')
                break

            if self._is_to_sync_networks(frame_index):
                self._sync_networks()

            if self._is_to_train_network(frame_index):
                for _ in range(Training.EPOCHS):
                    batch = self._buffer.sample(Training.BATCH_SIZE)
                    loss = self._fit(batch)
                    losses.append(loss)

        save_name = f'checkpoints/last_dqn_{self._best_mean_reward}/checkpoint'
        self._tgt_net.save_weights(save_name)
        self._env.quit()
        return losses
