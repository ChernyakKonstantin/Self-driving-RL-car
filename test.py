import pygame

import environment_new
import radar

env = environment_new.Environment()

pygame.init()
SIZE = 700, env.WORLD_LENGTH + 50
surface = pygame.display.set_mode(SIZE)

car_track = []

FPS = 30
fpsClock = pygame.time.Clock()

view = env.reset()

is_done = False
total_reward = 0.0
while not is_done:
    car_track.append((env.car._x, env.car._y))
    env.render(surface)
    for dot in car_track:
        pygame.draw.circle(surface, (255, 255, 255), (int(dot[0]), int(dot[1])), 1)
    radar.show(surface, view)
    pygame.display.flip()

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        view, reward, is_done, _ = env.step(3)
        total_reward += reward

    elif keys[pygame.K_RIGHT]:
        view, reward, is_done, _ = env.step(2)
        total_reward += reward

    if keys[pygame.K_UP]:
        view, reward, is_done, _ = env.step(1)
        total_reward += reward
    else:
        view, reward, is_done, _ = env.step(0)
        total_reward += reward

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_done = True

print(total_reward)
pygame.quit()
