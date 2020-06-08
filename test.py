import pygame
import environment_new
import math
import random
import radar


#def allowed(view):
#    if min(view) > 5:
#        return True
#    else:
#        return False
#    
#def generate_world():
#    OBSTCL_SIZE = [100,100]
#    obstacles = []
#    for _ in range(30):
#        x = random.randint(0, SIZE[0])
#        y = random.randint(0, SIZE[1])
#        w = random.randint(0, OBSTCL_SIZE[0])
#        h = random.randint(15, OBSTCL_SIZE[1])
#        obstcl = obstacle.Obstacle((x,y),(w,h))
#        obstacles.append(obstcl)
#    return obstacles    
#
#def get_walls(obstacles):
#    walls = []
#    for obst in obstacles:
#        for wall in obst.edges:
#            walls.append(wall)
#    return walls
#            
#    

#INIT_X = 300
#INIT_Y = 0
#BLACK = (0, 0, 0)

env = environment_new.Environment()

pygame.init()
SIZE = 700, env.WORLD_LENGTH + 50
surface = pygame.display.set_mode(SIZE)

#car = car.Car(INIT_X, INIT_Y)

#done = False

car_track = []

FPS = 30
fpsClock = pygame.time.Clock()

#obstacles = generate_world()
#walls = get_walls(obstacles)

view = env.reset()

is_done = False
total_reward = 0.0
while not is_done:
    car_track.append((env.car.pos_x, env.car.pos_y))
    

            
    
#    view = car.sensor.get_view(walls)



    
    #surface.fill(BLACK)  


#    for obst in obstacles:
#        obst.show(surface)
    

        
    
#    car.sensor.show(surface)
    env.render(surface)
    for dot in car_track:
        pygame.draw.circle(surface, (255,255,255), (int(dot[0]), int(dot[1])), 1)
    radar.show(surface, view)
    pygame.display.flip()
    
    keys = pygame.key.get_pressed()
    
    if keys[pygame.K_LEFT]:
#        if allowed(view):
#            car.move_left()
        view,reward,is_done,_ = env.step(1)
        total_reward += reward

    if keys[pygame.K_RIGHT]:
#        if allowed(view):
#            car.move_right()
        view,reward,is_done,_ = env.step(2)
        total_reward += reward
        
    if keys[pygame.K_UP]:
#        if allowed(view):
#            car.move_forward()
          view,reward,is_done,_ = env.step(0)
          total_reward += reward
#    view,reward,is_done,_ = env.step(random.randint(0,2))    
#    total_reward += reward       
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_done = True

print(total_reward)        
pygame.quit()