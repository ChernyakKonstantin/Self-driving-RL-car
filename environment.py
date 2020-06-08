#Придумать нормальную генерацию уровней

import random
import math

#Импорт элементов среды
import car
import obstacle

class Environment:
    WORLD_LENGTH = 650 #см
    WORLD_WIDTH = 300 #см
    INIT_X = WORLD_WIDTH / 2 #Начальное положение автомобиля
    INIT_Y = 10              #
    MIN_SIZE = 10 #Размеры препятствий
    MAX_SIZE = 80 #
    N = 40 #Число препятствий
    START_Y = 30 #Начало зоны генерации препятствий
    
    
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
        self.observation = self.next_observation        
        if self.no_collision(self.observation):
            self.actions[action]() #Выполнить действие
            self.next_observation = self.get_observation() 
            reward = self.get_reward()
            #reward -= reward * self.observation[59] / 200 #Чем ближе центр машины к препятствию, тем меньше награда
            is_done = False
        else:
            self.next_observation = self.get_observation()
            reward = -130
            is_done = True
        return self.next_observation, reward, is_done, None #None, чтобы не переписывать агентов
    
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
        if min(observation) > 5:#self.car.radius: #Если расстояние до препятствия
            return True                        #меньше радиуса разворота автомобиля,
        else:                                  #то столкновение неизбежно
            return False
    
    def get_reward(self):
        reward = self.car.pos_y - self.car_old_pos
        if reward < 0: reward = 10 * reward
        self.car_old_pos = self.car.pos_y
        return reward
    
    def sample(self):
        return random.randint(0, 2)
    
    def render(self, surface): #Отрисовка среды
        surface.fill((0,0,0)) #Black color
        for obst in self.obstacles:
            obst.show(surface)
        self.car.sensor.show(surface)