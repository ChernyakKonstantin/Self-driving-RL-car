import torch
import numpy as np

from net import myDQN
from agent import Agent
from experience_buffer import ExperienceBuffer
from loss import loss_func
from environment_new import Environment

from radar import show

N_INPUT = 30 
N_HIDDEN = 256
N_OUTPUT = 3

MEAN_REWARD_BOUND = 500
GAMMA = 0.99
BATCH_SIZE = 32
REPLAY_SIZE = 10**4
LEARNING_RATE = 0.001
SYNC_TARGET_FRAMES = 4 * 10**3
REPLAY_START_SIZE = 10**3

EPSILON_DECAY_LAST_FRAME = 10**4
EPSILON_START = 1.0
EPSILON_FINAL = 0.02

env = Environment()
net = myDQN(N_INPUT, N_HIDDEN, N_OUTPUT).to("cuda")
tgt_net = myDQN(N_INPUT, N_HIDDEN, N_OUTPUT).to("cuda")

#net.load_state_dict(torch.load("dqn.pt")) #Загрузка весов для 
#net.eval()                                #продолжения обучения
#tgt_net.load_state_dict(torch.load("dqn.pt")) #
#tgt_net.eval()                                #

buffer = ExperienceBuffer(REPLAY_SIZE)
agent = Agent(env, buffer)
epsilon = EPSILON_START

optimizer = torch.optim.Adam(net.parameters())

total_rewards = []
best_mean_reward = None
frame_idx = 0

import pygame
pygame.init()
SIZE = 700, env.WORLD_LENGTH + 50
surface = pygame.display.set_mode(SIZE)
done = False
losses = []

while not done :
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            done = True
    
    frame_idx += 1
    
    epsilon = max(EPSILON_FINAL, EPSILON_START - frame_idx / EPSILON_DECAY_LAST_FRAME)
  
    reward = agent.play_step(net, epsilon)
    env.render(surface)
    show(surface, agent.state)
    pygame.display.flip()
  
    if reward is not None:
      total_rewards.append(reward)
      mean_reward = np.mean(total_rewards[-10:]) #Cредняя награда за послдение 10 игр


      #print("Frame %d: done %d games, reward %.3f, eps %.2f" % (frame_idx ,len(total_rewards), total_rewards[-1], epsilon))
      if best_mean_reward is None or best_mean_reward < mean_reward:
          if best_mean_reward is not None:
            print("Best mean reward updated %.3f -> %.3f, model saved" % (best_mean_reward, mean_reward))
            model_save_name = 'dqn' + str(len(total_rewards)) + '.pt'
            torch.save(tgt_net.state_dict(), model_save_name)
          best_mean_reward = mean_reward
      if mean_reward > MEAN_REWARD_BOUND:
          print("Solved in %d frames!" % frame_idx)
          break

    if len(buffer) < REPLAY_START_SIZE:
      continue

    if frame_idx % SYNC_TARGET_FRAMES == 0:
          tgt_net.load_state_dict(net.state_dict())
          print("SYNCHRONIZED")

    optimizer.zero_grad()
    batch = buffer.sample(BATCH_SIZE)
    loss = loss_func(batch, net, tgt_net, GAMMA)
    losses.append(loss.item())
    if frame_idx % 1000 == 0:
        print("MEAN_LOSS_VALUE: " + str(np.mean(losses[-1000:])))
    loss.backward()
    optimizer.step()
    
pygame.quit()
torch.save(tgt_net.state_dict(), "LAST.pt")