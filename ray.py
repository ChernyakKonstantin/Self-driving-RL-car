import pygame
import math


class Ray: #Класс луча
    def __init__(self, x, y, max_ray_len):
        self.sourse_pos = [x,y] #Координаты источника луча
        self.max_ray_len = max_ray_len
        self.end_pos = [None,None] #Координаты конечной точки луча
        self.intersection_pt = [None, None] #Координаты точки пересечения с препятствием      
    
    def translate(self, x, y):         #Переводит относительные от источника 
        new_x = self.sourse_pos[0] + x  #луча координаты в абсолютные
        new_y = self.sourse_pos[1] + y
        return new_x, new_y
    
    def cast(self, line): #Если луч пересекает объект, возвращает координаты 
                          #точки пересечения, в противном случае None
                          #Википедия: пересечение прямых
        x1 = line.a[0] #x coord of a of the line
        y1 = line.a[1] #y coord of a of the line 
        x2 = line.b[0] #x coord of b of the line
        y2 = line.b[1] #y coord of b of the line
        
        x3 = self.sourse_pos[0] #x coord of the ray sourse
        y3 = self.sourse_pos[1] #y coord of the ray sourse
        x4 = self.end_pos[0] #x coord of the ray end
        y4 = self.end_pos[1] #y coord of the ray end
        
        den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4) 
        if den == 0: return None
    
        t = ((x1 - x3) * (y3 - y4) - (y1 - y3) * (x3 - x4)) / den

        if (t > 0 and t < 1):
            x = x1 + t * (x2 - x1)
            y = y1 + t * (y2 - y1)
            x = int(x)
            y = int(y)
            if (x < self.sourse_pos[0] and x > self.end_pos[0]) or (x > self.sourse_pos[0] and x < self.end_pos[0]): #Проверка, что точка
                                                                                                                     #пересечения находится
                                                                                                                     #по направлению взгяда
                self.intersection_pt = x,y
                return x,y
            else: 
                return None
        else:
            self.intersection_pt = None
            return None 
        
    def look_at(self, x, y): #Переместить конец луча
        self.end_pos[0] = x 
        self.end_pos[1] = y
        
    def upd_sourse_coord(self, x, y): #Обновить координаты источника луча
        self.sourse_pos[0] = x
        self.sourse_pos[1] = y
    
    def get_distance(self):  #Дистанция до точки пересечения
        x = self.intersection_pt[0] - self.sourse_pos[0]
        y = self.intersection_pt[1] - self.sourse_pos[1]
        return math.sqrt(pow(x,2) + pow(y,2))
    
    def show(self,surface): #Отрисовать луч
        WHITE = (255,255,255)
        if self.intersection_pt and self.get_distance() <= self.max_ray_len: # Отрисовать луч до точки пересечения,
                                                                             # если такая существует и находится
                                                                             # в пределах дальности луча
            pygame.draw.line(surface, 
                         WHITE,
                         self.sourse_pos,
                         self.intersection_pt)
        else: #Иначе отрисовать до конечной точки луча
            pygame.draw.line(surface, 
                             (255,255,255), #White color
                             self.sourse_pos,
                             self.end_pos)
    
