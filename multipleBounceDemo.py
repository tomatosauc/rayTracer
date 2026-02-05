import tkinter
from math import sqrt, sin, cos, acos, pi
from random import *

canvas = tkinter.Canvas(width=600,height=600)
canvas.pack()

class Circle:
    def __init__(self, center: tuple[float, float], radius, ):
        self.center_x = center[0]
        self.center_y = center[1]
        self.radius = radius
        self.center_vector = Vector2(center)

    def __call__(self):
        return ((self.center_x-self.radius,self.center_y-self.radius),(self.center_x+self.radius,self.center_y+self.radius))

class Vector2:
    def __init__(self, vector:tuple[float, float]):
        self.size = sqrt(vector[0]**2+vector[1]**2)
        try:
            self.direction = (vector[0]/self.size, vector[1]/self.size)
        except Exception:
            self.direction = (0,0)
    
    def dot(self, vector:'Vector2'):
        return round(self.size*vector.size*(self.direction[0]*vector.direction[0]+self.direction[1]*vector.direction[1]),8)
    
    def add(self, vector:'Vector2'):
        return Vector2((round(self.size*self.direction[0]+vector.size*vector.direction[0],8),round(self.size*self.direction[1]+vector.size*vector.direction[1],8)))
    
    def sub(self, vector:'Vector2'):
        return Vector2((round(self.size*self.direction[0]-vector.size*vector.direction[0],8),round(self.size*self.direction[1]-vector.size*vector.direction[1]),8))
    
    def mul(self, scalar:float):
        vec = self()
        return Vector2((vec[0]*scalar,vec[1]*scalar))
    
    def rotate(self, angle:float):
        vec = self()
        angle *= -1
        return Vector2((round(vec[0]*cos(angle)-vec[1]*sin(angle),8),round(vec[0]*sin(angle)+vec[1]*cos(angle),8)))
    
    def rotateDeg(self, angle:float):
        angle = -angle/360*2*pi
        vec = self()
        return Vector2((round(vec[0]*cos(angle)-vec[1]*sin(angle),8),round(vec[0]*sin(angle)+vec[1]*cos(angle),8)))

    def __str__(self):
        return f"Vector2({self.size*self.direction[0]}, {self.size*self.direction[1]})"
    
    def __call__(self):
        return (self.size*self.direction[0], self.size*self.direction[1])

class Ray:
    def __init__(self, origin:'Vector2', direction:'Vector2', bounceCounter:int = 0):
        self.origin = origin
        self.direction = direction
        self.direction.size = 1
        self.bounceCounter = bounceCounter
    
    def rot(self, angle:float):
        # Rotate by radians
        self.direction = self.direction.rotate(angle)

    def rotDeg(self, angle:float):
        # Rotate by degrees
        self.direction = self.direction.rotateDeg(angle)

    def __str__(self):
        return f"Ray(({self.origin.size*self.origin.direction[0]}, {self.origin.size*self.origin.direction[1]}), ({self.direction.direction[0]}, {self.direction.direction[1]}))"
    
    def __call__(self):
        return (self.origin, self.direction)
    
circle = Circle((300, 300), 100)

ray_origin = Vector2((500, 300))

update_list: list['Ray'] = []

circles = [circle]

FOV = 90
ROTATION = 175
NUM_OF_RAYS = 50
BOUNCES = 1

for angle in range(int((ROTATION-FOV/2)*100), int((ROTATION+FOV/2+1)*100), int(FOV/NUM_OF_RAYS*100)):
    angle/=100
    ray = Ray(origin=ray_origin, direction=Vector2((1,0)))
    ray.rotDeg(angle)
    update_list.append(ray)

for circle in circles:
    canvas.create_oval(circle())

while True:
    if update_list == []:
        break
    else:
        workingRay = update_list.pop(0)
        for circle in circles:
            vectorToCircleCenter = circle.center_vector.sub(workingRay.origin)
            rayProjection = workingRay.direction.dot(vectorToCircleCenter)
            rayCenterDistance = sqrt(round(vectorToCircleCenter.size**2-rayProjection**2,8))
            if vectorToCircleCenter.size > circle.radius:
                if circle.radius - rayCenterDistance > 0 and rayProjection > 0:
                    intersectionToCenterSize = sqrt(circle.radius**2-rayCenterDistance**2)
                    hit_point = [origin_coord+dir_coord*(rayProjection-intersectionToCenterSize) for origin_coord, dir_coord in zip(workingRay.origin(), workingRay.direction())]
                    canvas.create_rectangle(hit_point, hit_point, outline='red',fill='red')
                    canvas.create_line(workingRay.origin(), hit_point, fill='blue')
                    normalVector = Vector2(tuple(hit_point)).sub(workingRay.origin)
                    normalVector.size = 1
                    #if workingRay.bounceCounter+1 < BOUNCES:
                    #    newRay = Ray(Vector2(tuple(hit_point)), Vector2((1,0)), workingRay.bounceCounter+1)
                    #    update_list.append(newRay)
                else:
                    canvas.create_line(workingRay.origin(), [origin+direction*500 for origin, direction in zip(workingRay.origin(), workingRay.direction())], fill="black")
            else:
                intersectionToCenterSize = sqrt(circle.radius**2-rayCenterDistance**2)
                hit_point = [origin_coord+dir_coord*(rayProjection+intersectionToCenterSize) for origin_coord, dir_coord in zip(workingRay.origin(), workingRay.direction())]
                canvas.create_rectangle(hit_point, hit_point, outline='red',fill='red')
                canvas.create_line(workingRay.origin(), hit_point, fill='blue')
                #if workingRay.bounceCounter+1 < BOUNCES:
                #    newRay = Ray(Vector2(tuple(hit_point)), Vector2((1,0)), workingRay.bounceCounter+1)
                #    update_list.append(newRay)


canvas.mainloop()