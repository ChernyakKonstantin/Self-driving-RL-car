import numpy as np
import collections
import torch

Experience = collections.namedtuple('Experience', field_names=['state', 'action', 'reward', 'done', 'new_state'])

class Agent:
    def __init__(self, env, exp_buffer):
        self.env = env #Среда в которой играет агент
        self.exp_buffer = exp_buffer
        self._reset()

    def _reset(self):
        self.state = self.env.reset()
        self.total_reward = 0.0

    def play_step(self, net, epsilon=0.0):
        done_reward = None

        if np.random.random() < epsilon: #выбор случайного действия с вероятность epsilon
            action = self.env.sample()
        else: #Выбор действия, максимизирующего Q
            state_v = torch.FloatTensor([self.state]).to("cuda") 
            q_vals_v = net(state_v)
            _, act_v = torch.max(q_vals_v, dim=1)
            action = int(act_v.item())

        # do step in the environment
        new_state, reward, is_done, _ = self.env.step(action)
        self.total_reward += reward

        exp = Experience(self.state, action, reward, is_done, new_state) #Named tuple
        self.exp_buffer.append(exp) #Сохранить данные в Experience Buffer
        self.state = new_state
        if is_done:
            done_reward = self.total_reward
            self._reset()
        return done_reward

    def play(self, net):
      state_v = torch.FloatTensor([self.state]).to("cuda")
      q_vals_v = net(state_v)
      _, act_v = torch.max(q_vals_v, dim=1)
      action = int(act_v.item())
      new_state, reward, is_done, _ = self.env.step(action)
      self.state = new_state
      self.total_reward += reward
      if is_done:
        done_reward = self.total_reward
        print('REWARD: ', done_reward)
        self._reset()