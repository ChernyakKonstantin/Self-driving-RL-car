#Придумать нормальную генерацию уровней

import random
import math

#Импорт элементов среды
import car
from obstacle import Line

class Environment:
    WORLD_LENGTH = 650 #см
    WORLD_WIDTH = 300 #см
    INIT_X = WORLD_WIDTH / 2 #Начальное положение автомобиля
    INIT_Y = 10              #
    ROAD_WIDTH = 50
    START_X = INIT_X - ROAD_WIDTH / 2
    START_Y = 5
    X_SHIFT = 15
    Y_SHIFT = 30  
    
    def __init__(self):
        self.car = car.Car(Environment.INIT_X, Environment.INIT_Y)
        self.actions = [self.car.move_forward, #Возможные действия
                          self.car.move_left,
                          self.car.move_right]
        n_actions = len(self.actions)

        self.walls = []
        self.generate_world()   
        
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
        first_point = (Environment.START_X, Environment.START_Y)
        while first_point[1] < Environment.WORLD_LENGTH:
            second_point_x = first_point[0] + random.choice([-1,1]) * random.randint(0, Environment.X_SHIFT)
            second_point_y = first_point[1] + random.randint(0, Environment.Y_SHIFT)
            second_point = (second_point_x, second_point_y)
            self.walls.append(Line(*first_point, *second_point))
            first_point = second_point
        n_walls = len(self.walls)
        for index in range(n_walls):
            self.walls.append(self.walls[index].shifted_copy(Environment.ROAD_WIDTH))
        
        #Создадим границы мира
        self.walls.append(Line(*(0, Environment.START_Y), #Верхняя граница
                               *(Environment.WORLD_WIDTH, Environment.START_Y)))
        
        self.walls.append(Line(*(0, Environment.WORLD_LENGTH), #Нижняя граница
                               *(Environment.WORLD_WIDTH, Environment.WORLD_LENGTH)))       

    
    def get_observation(self): #Возвращает наблюдения
        return self.car.sensor.get_view(self.walls)
    
    def no_collision(self, observation): #Проверяет, может ли дальше двигаться автомобиль
        if min(observation) > 5:#self.car.radius: #Если расстояние до препятствия
            return True                        #меньше радиуса разворота автомобиля,
        else:                                  #то столкновение неизбежно
            return False
    
    def get_reward(self):
        reward = self.car.pos_y - self.car_old_pos
#        if reward < 0: reward = 10 * reward
        self.car_old_pos = self.car.pos_y
        return reward
    
    def sample(self):
        return random.randint(0, 2)
    
    def render(self, surface): #Отрисовка среды
        surface.fill((0,0,0)) #Black color
        for wall in self.walls:
            wall.show(surface)
        self.car.sensor.show(surface)