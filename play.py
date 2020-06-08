import torch

import pygame

from net import myDQN
from agent import Agent
from experience_buffer import ExperienceBuffer
from environment
 import Environment

from radar import show

N_INPUT = 30 
N_HIDDEN = 256
N_OUTPUT = 3

REPLAY_SIZE = 10**4 #Приходится оставить из-за структуры агента

env = Environment()
net = myDQN(N_INPUT, N_HIDDEN, N_OUTPUT).to("cuda")
net.load_state_dict(torch.load("dqn1605.pt"))
net.eval()
buffer = ExperienceBuffer(REPLAY_SIZE)
agent = Agent(env, buffer)

pygame.init()
SIZE = 700, env.WORLD_LENGTH + 50
surface = pygame.display.set_mode(SIZE)
is_done = False
#agent._reset()
while not is_done:
    env.render(surface)
    show(surface, agent.state)   

    pygame.display.flip()
    
    keys = pygame.key.get_pressed()
    
    is_done = agent.play(net)   
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_done = True

      
pygame.quit()