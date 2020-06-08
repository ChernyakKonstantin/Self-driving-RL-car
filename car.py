#НЕКОРРЕКТО РАБОТАЕТ ОТРИСОВКА МАШИНЫ

import sensor
import math
import pygame


class Car:
    WIDTH = 10 #Ширина автомобиля в см, 1см = 1px
    LENGTH = 20 #Длина автомобиля в см, 1см = 1px
    RADIUS = 15 #Радиус поворота автомобиля, см
    VELOCITY = 1 #Скорость автомобиля см/с
    AOV = 120 #Угол обзора сенсора, градусы
    MAX_RAY_LEN = 200 #Дальность луча, см
    INIT_ORIENTATION = 0 #Градусы #Автомобиль перпендикуляр оси X
    
    
    def __init__(self, x, y):        
        self.width = Car.WIDTH
        self.radius = Car.RADIUS
        self.velocity = Car.VELOCITY
        self.ang_velocity = self.velocity / self.radius #Угловая скорость рад/с
        self.width = Car.WIDTH
        self.pos_x = x
        self.pos_y = y
        self.orientation = math.radians(Car.INIT_ORIENTATION)
        self.sensor = sensor.Sensor(Car.AOV, Car.MAX_RAY_LEN, self.pos_x, self.pos_y, self.orientation)
#        self.original_image = pygame.image.load('car.png')
#        self.image = self.original_image
        
    def move_forward(self):
        self.pos_y += self.velocity * math.cos(self.orientation) #Автомобиль движется сверху вниз
        self.pos_x += self.velocity * math.sin(self.orientation)
        self.sensor.upd_pos(self.pos_x, self.pos_y)        
        
    def move_left(self):
        rotation_angle = self.calc_angle()
        self.orientation += rotation_angle
        self.sensor.upd_ray_limits(rotation_angle)
        self.sensor.orientation = self.orientation
        self.move_forward()
    
    def move_right(self):
        rotation_angle = self.calc_angle()
        self.orientation -= rotation_angle
        self.sensor.upd_ray_limits(-1 * rotation_angle)
        self.sensor.orientation = self.orientation
        self.move_forward()
        
    def calc_angle(self): #Длина хорды дуги при повороте автомобиля
        arc_angle = self.ang_velocity #Угол дуги, описываемой при повороте
        rotation_angle = arc_angle / 2 #Угол отклонения автомобиля при повороте
        return  rotation_angle
    
    def show(self, surface): #Некорректно работает
        """
        При отрисовке сдвигает точка верхняя левая
        """
        #WHITE = (255, 255, 255)
        self.image = pygame.transform.rotate(self.original_image, math.degrees(self.orientation))
        rect = self.image.get_rect()
        left = self.pos_x - 15 #* math.sin(90 - math.degrees(self.orientation)) #!!!!
        #print(left)
        surface.blit(self.image, (left, self.pos_y))      
#        rect = pygame.Rect(left, self.pos_y, self.width, self.width*1.3)
#        rect = pygame.transform.rotate(rect, self.orientation)
#        pygame.draw.rect(surface, WHITE, rect)
        