import pygame
import math

def show(surface, view): #Отрисовка карты   
    red = (255,0,0)
    green = (0,255,0)
    white = (255,255,255)
    x = 400
    y = 400
    diameter = 200
    radius = 1
    
    forbidden_radius = 5 #Пока здесь вручную ввожу
    
    for dot in enumerate(view):
        if dot[1]:
            angle = math.radians(4*dot[0] + 120)
            distance = diameter/2 * (dot[1] / 200)
#            center = (int(x + diameter/2 + distance * math.sin(angle)), int(y + diameter/2 + distance * math.cos(angle)))
#        
#            pygame.draw.circle(surface,
#                               red,
#                               center,
#                               radius)
            start_point = (int(x + diameter/2 + distance * math.sin(angle)), 
                           int(y + diameter/2 + distance * math.cos(angle)))
            
            end_point = (int(x + diameter/2 + diameter/2 * math.sin(angle)), 
                           int(y + diameter/2 + diameter/2 * math.cos(angle)))
        
            pygame.draw.line(surface,
                             red,
                             start_point,
                             end_point,
                             1)    
    #Граница обзора        
    pygame.draw.arc(surface,
                    green,
                    pygame.Rect(x,y,diameter,diameter),
                    math.radians(30),
                    math.radians(150),
                    2)
    
    #Запрещенная зона
    pygame.draw.arc(surface,
                    white,
                    pygame.Rect(x + diameter /2 - forbidden_radius,
                                y + diameter / 2 - forbidden_radius,
                                forbidden_radius*2,
                                forbidden_radius*2),
                    math.radians(30),
                    math.radians(150),
                    2)    
    
    #Левая граница обзор    
    pygame.draw.line(surface,
                     green,
                     (x + diameter /2, 
                      y + diameter / 2),
                     (x + diameter / 2 + diameter / 2* math.sin(math.radians(120)), 
                      y + diameter / 2 + diameter / 2* math.cos(math.radians(120))),
                      2)
    #Правая граница обзора                 
    pygame.draw.line(surface, 
                     green,
                     (x + diameter /2, 
                      y + diameter / 2),
                     (x + diameter / 2 + diameter / 2* math.sin(math.radians(240)), 
                      y + diameter / 2 + diameter / 2* math.cos(math.radians(240))),
                      2)
    #Центральная линия
    pygame.draw.line(surface, 
                     green,
                     (x + diameter /2, 
                      y + diameter / 2),
                      (x + diameter / 2, 
                      y),
                      1)                    
                     
                    
    
