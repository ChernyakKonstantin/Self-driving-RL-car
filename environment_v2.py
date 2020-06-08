"""Теперь step() выполняет действие N шагов подряд"""

#Придумать нормальную генерацию уровней

import random
import math

#Импорт элементов среды
import car
import obstacle

class Environment:
    WORLD_LENGTH = 750 #см
    WORLD_WIDTH = 300 #см
    INIT_X = WORLD_WIDTH / 2 #Начальное положение автомобиля
    INIT_Y = 5              #
    MIN_SIZE = 10 #Размеры препятствий
    MAX_SIZE = 80 #
    N = 40 #Число препятствий
    START_Y = 10 #Начало зоны генерации препятствий
    N_STEPS = 3 #Число шагов, в течении которых повторится действие
    
    
    def __init__(self):
        self.car = car.Car(Environment.INIT_X, Environment.INIT_Y)
        self.actions = [self.car.move_forward, #Возможные действия
                          self.car.move_left,
                          self.car.move_right]
        n_actions = len(self.actions)
        
        self.obstacles = []
        self.generate_world()
        
        self.walls = []
        self.get_walls()   
        
        self.car_old_pos = Environment.INIT_Y
    
    def reset(self): 
        self.__init__()
        self.next_observation = self.get_observation()
        return self.next_observation
    
    def step(self, action):
        stack_reward = 0
        next_obs_stack = []
        for frame in range(Environment.N_STEPS):
            self.observation = self.next_observation 
            if self.no_collision(self.observation):
                self.actions[action]() #Выполнить действие
                self.next_observation = self.get_observation()
                next_obs_stack.append(self.next_observation) #NEW
                stack_reward += self.get_reward()
                is_done = False
            else:
                self.next_observation = self.get_observation()
                next_obs_stack.append(self.next_observation) #NEW
                stack_reward += 0
                is_done = True
                for _ in range(Environment.N_STEPS - 1 - frame):
                    next_obs_stack.append(self.next_observation)
                break
                
            
                
        return next_obs_stack, stack_reward, is_done, None #None, чтобы не переписывать агентов
    
    def generate_world(self): #Генерирует новый мир
        #random.seed(3)
        VERT_BORDERS_SIZE = (1, Environment.WORLD_LENGTH + 1)#+1 т.к. y = -1
        HOR_BORDERS_SIZE = (Environment.WORLD_WIDTH, 1)
        
        #Создадим границы мира
        self.obstacles.append(obstacle.Obstacle((0, -1), #y = -1, чтобы не было конфликта с сенсором
                                               HOR_BORDERS_SIZE))
        self.obstacles.append(obstacle.Obstacle((0, Environment.WORLD_LENGTH),
                                                HOR_BORDERS_SIZE))
        self.obstacles.append(obstacle.Obstacle((-1, -1), #x = -1, чтобы границы не заходила на поле
                                                VERT_BORDERS_SIZE)) 
        self.obstacles.append(obstacle.Obstacle((Environment.WORLD_WIDTH, -1),
                                                VERT_BORDERS_SIZE))
        for _ in range(Environment.N):
            x_pos = random.randint(0, Environment.WORLD_WIDTH)
            y_pos = random.randint(Environment.START_Y, Environment.WORLD_LENGTH)
            width = random.randint(Environment.MIN_SIZE, Environment.MAX_SIZE)
            length = random.randint(Environment.MIN_SIZE, Environment.MAX_SIZE)
            self.obstacles.append(obstacle.Obstacle((x_pos, y_pos),
                                                    (width, length)))
    
    def get_walls(self):
        for obst in self.obstacles:
            for wall in obst.edges:
                self.walls.append(wall)
    
    def get_observation(self): #Возвращает наблюдения
        return self.car.sensor.get_view(self.walls)
    
    def no_collision(self, observation): #Проверяет, может ли дальше двигаться автомобиль
        if min(observation) > 5 / math.cos(math.radians(30)):#self.car.radius: #Если расстояние до препятствия
            return True                        #меньше радиуса разворота автомобиля,
        else:                                  #то столкновение неизбежно
            return False
    
    def get_reward(self):
        reward = self.car.pos_y - self.car_old_pos
        self.car_old_pos = self.car.pos_y
        return reward
    
    def sample(self):
        return random.randint(0, 2)
    
    def render(self, surface): #Отрисовка среды
        surface.fill((0,0,0)) #Black color
        for obst in self.obstacles:
            obst.show(surface)
        self.car.sensor.show(surface)