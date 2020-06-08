import pygame

class Line:  #Класс линий, из которых состоит препятствие
    def __init__(self, x1, y1, x2, y2): 
        self.a = x1,y1
        self.b = x2,y2
        
    def shifted_copy(self, shift):
        a = self.a[0] + shift, self.a[1]
        b = self.b[0] + shift, self.b[1]
        return Line(*a,*b)
        
    def show(self, surface):
        pygame.draw.line(surface, 
                         (255,255,255), #White color
                         self.a,
                         self.b)

class Obstacle: #Класс препятствия
    def __init__(self, coord, size):
        self.coord = coord #x,y
        self.size = size #width, height
        self.edges = []
        self.make_object()
        
    def make_object(self): #Создает прямоугольный объект
        self.edges.append(Line(self.coord[0], 
                          self.coord[1], 
                          self.coord[0] + self.size[0], 
                          self.coord[1]))
        self.edges.append(Line(self.coord[0] + self.size[0], 
                          self.coord[1], 
                          self.coord[0] + self.size[0], 
                          self.coord[1] + self.size[1]))
        self.edges.append(Line(self.coord[0], 
                          self.coord[1] + self.size[1], 
                          self.coord[0] + self.size[0], 
                          self.coord[1] + self.size[1]))
        self.edges.append(Line(self.coord[0], 
                          self.coord[1], 
                          self.coord[0], 
                          self.coord[1] + self.size[1]))
    
    def show(self, surface):
        for edge in self.edges:
            edge.show(surface)
            