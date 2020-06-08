import math
import pygame

import ray

class Sensor:
    def __init__(self, aov, max_ray_len, x, y, orientation):
        self.aov = aov #Угол обзора в градусах
        self.angle_step_degree = 4
        self.angle_step = math.radians(self.angle_step_degree) #Шаг поворота датчика равен 1 градус
                                          #в радианах
        self.pos_x = x
        self.pos_y = y        
        self.max_ray_len = max_ray_len #Максимальная дальность луча
        self.ray = ray.Ray(self.pos_x, self.pos_y, self.max_ray_len)
        self.orientation = orientation #Направление центра
        self.left_limit = math.radians(self.orientation + self.aov / 2) #Крайнее левое
                                                                        #значение угла
        self.right_limit = math.radians(self.orientation - self.aov / 2) #Крайнее правое
                                                                         #значение угла
                                                                         
    def get_view(self, obstacles): #Получить с сенсора данные об окружении
        view = [] #Карта мира
        angle = self.right_limit #Начальный угол
        for cur_angle in range(0, self.aov, self.angle_step_degree): 
            ray_end_x = math.sin(angle) * self.max_ray_len #Получить относительные
            ray_end_y = math.cos(angle) * self.max_ray_len #координаты конца луча     
            ray_end_x, ray_end_y = self.ray.translate(ray_end_x, ray_end_y) # Перевести относительные коррдинаты
                                                                            # конца луча в абсолютные
            self.ray.look_at(ray_end_x, ray_end_y) #Перенести конец луча в новую точку
            distance = self.get_distance(obstacles) #Получить дистанцию до объекта          
            view.append(distance) #Записать данные
            angle += self.angle_step
        return view
            
    def get_distance(self, obstacles): #Определить расстояние до точки пересечения
        closest = self.max_ray_len 
        record = self.max_ray_len #Максимально возможное для регистрации 
                                  #расстояние до точки пересечения
                                  
        for obstacle in obstacles: #Перебрать все границы препятсвий
            pt = self.ray.cast(obstacle) #Найти точку пересечения с границей
                                         #препятствия
            if pt: #Если такая точка существует
                distance = self.ray.get_distance() #Найти расстояние до нее
                if distance <= record:
                    record = distance
                    closest = record
        return closest
    
    def upd_pos(self, x, y):
         self.pos_x = x
         self.pos_y = y
         self.ray.upd_sourse_coord(self.pos_x, self.pos_y)
    
    def upd_ray_limits(self, delta):
        self.left_limit += delta
        self.right_limit += delta
        
    def show(self, surface): #Отрисовка поля зрения сенсора
        x_r = math.sin(self.right_limit) * self.max_ray_len
        y_r = math.cos(self.right_limit) * self.max_ray_len
        
        coord_r = self.ray.translate(x_r, y_r) #координаты конца правой грани
        
        x_l = math.sin(self.left_limit) * self.max_ray_len
        y_l = math.cos(self.left_limit) * self.max_ray_len
        
        coord_l = self.ray.translate(x_l, y_l) #координаты конца правой грани
        
        x_c = math.sin(self.orientation) * self.max_ray_len
        y_c = math.cos(self.orientation) * self.max_ray_len
        
        coord_c = self.ray.translate(x_c, y_c)
        
        coord_30 = self.ray.translate(math.sin(self.orientation - math.radians(30)) * self.max_ray_len, 
                                       math.cos(self.orientation - math.radians(30)) * self.max_ray_len)
        
        coord_90 = self.ray.translate(math.sin(self.orientation + math.radians(30)) * self.max_ray_len, 
                                       math.cos(self.orientation + math.radians(30)) * self.max_ray_len)
        
        pygame.draw.line(surface, 
                        (255,0,0), #Red color
                        (self.pos_x, self.pos_y),
                        coord_r)
        
        pygame.draw.line(surface, 
                             (0,255,0), #Green color
                             (self.pos_x, self.pos_y),
                             coord_l)
        
        pygame.draw.line(surface, 
                             (255,255,255), #White color
                             (self.pos_x, self.pos_y),
                             coord_c)
        
        pygame.draw.line(surface, 
                             (255,255,100), #Yellow color
                             (self.pos_x, self.pos_y),
                             coord_30)
        
        pygame.draw.line(surface, 
                             (150,50,150), #Purple color
                             (self.pos_x, self.pos_y),
                             coord_90)
        
        pygame.draw.arc(surface,
                        (255,0,0),
                        pygame.Rect(self.pos_x - self.max_ray_len, 
                                    self.pos_y - self.max_ray_len, 
                                    self.max_ray_len * 2, 
                                    self.max_ray_len * 2),
                        self.orientation - math.radians(self.aov/2) - math.radians(90),
                        self.orientation + math.radians(self.aov/2) - math.radians(90))
