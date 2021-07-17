import collections

import numpy as np


class ExperienceBuffer:
    def __init__(self, capacity):
        self.buffer = collections.deque(
            maxlen=capacity)  # Список заданной длины, при превышении размера новые элементы "выдавят" самые первые

    def __len__(self):
        return len(self.buffer)

    def append(self, experience):
        self.buffer.append(experience)

    def sample(self, batch_size):
        indices = np.random.choice(len(self.buffer), batch_size,
                                   replace=False)  # Случайная выборка batch_size элементов из множества индексов элементов буфера
        states, actions, rewards, dones, next_states = zip(*[self.buffer[idx] for idx in indices])
        return np.array(states), np.array(actions), np.array(rewards, dtype=np.float32), \
               np.array(dones, dtype=np.uint8), np.array(next_states)
