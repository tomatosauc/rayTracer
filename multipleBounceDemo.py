import tkinter
from math import sqrt, sin, cos, acos, pi
from random import *
from uuid import uuid4

canvas = tkinter.Canvas(width=600,height=600)
canvas.pack()

class Circle:
    def __init__(self, center: tuple[float, float], radius, color: tuple[float, float, float]=(1,1,1)):
        self.center_x = center[0]
        self.center_y = center[1]
        self.radius = radius
        self.center_vector = Vector2(center)
        self.color = color

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
    def __init__(self, origin:'Vector2', direction:'Vector2', bounceCounter:int = 0, color:tuple[float, float, float] = (1,1,1), originalRay:'Ray'=None):
        self.id = uuid4()
        self.origin = origin
        self.direction = direction
        self.direction.size = 1
        self.bounceCounter = bounceCounter
        self.length = MAXIMUM_LENGTH
        self.color = color
        self.originalRay = originalRay
    
    def rot(self, angle:float):
        # Rotate by radians
        self.direction = self.direction.rotate(angle)

    def rotDeg(self, angle:float):
        # Rotate by degrees
        self.direction = self.direction.rotateDeg(angle)

    def __str__(self):
        return f"Ray({self.id})"
    
    def __call__(self):
        return (self.origin, self.direction)

def colorToHEX(color):
    return f"#{int(color[0]*255):02x}{int(color[1]*255):02x}{int(color[2]*255):02x}"

circle = Circle((300, 300), 250, color=(0.3,0.8,0.8))

ray_origin = Vector2((500, 300))

update_list: list['Ray'] = []

# Circle((300,0), 175, color=(0.9,0.5,0.1))

circles = [circle]

FOV = 120
ROTATION = 180
NUM_OF_RAYS = 200
BOUNCES = 1
MAXIMUM_LENGTH = 100000000

for angle in range(int((ROTATION-FOV/2)*100), int((ROTATION+FOV/2+1)*100), int(FOV/NUM_OF_RAYS*100)):
    angle/=100
    ray = Ray(origin=ray_origin, direction=Vector2((1,0)))
    ray.rotDeg(angle)
    update_list.append(ray)

for circle in circles:
    canvas.create_oval(circle(),outline=colorToHEX(circle.color))

while True:
    if update_list == []:
        break
    else:
        workingRay = update_list.pop(0)
        color = workingRay.color
        for circle in circles:
            vectorToCircleCenter = circle.center_vector.sub(workingRay.origin)
            rayProjection = workingRay.direction.dot(vectorToCircleCenter)
            rayCenterDistance = sqrt(round(vectorToCircleCenter.size**2-rayProjection**2,8))
            if vectorToCircleCenter.size >= circle.radius:
                if circle.radius - rayCenterDistance > 0 and rayProjection > 0:
                    intersectionToCenterSize = sqrt(circle.radius**2-rayCenterDistance**2)
                    relative_hit = Vector2(tuple([dir_coord*(rayProjection-intersectionToCenterSize) for dir_coord in workingRay.direction()]))
                    hit_point = [origin_coord+dir_coord*(rayProjection-intersectionToCenterSize) for origin_coord, dir_coord in zip(workingRay.origin(), workingRay.direction())]
                    hit_point_vector = Vector2(tuple(hit_point))
                    if relative_hit.size < workingRay.length:
                        if not workingRay.length >= MAXIMUM_LENGTH:
                            update_list.pop()
                        workingRay.length = relative_hit.size
                        workingRay.color = tuple([ray_component*circle_component for ray_component, circle_component in zip(color, circle.color)])
                        canvas.delete(workingRay.__str__())
                        # canvas.create_rectangle(hit_point, hit_point, outline='red',fill='red', tags=workingRay.__str__())
                        canvas.create_line(workingRay.origin(), hit_point, fill=colorToHEX(workingRay.color), tags=workingRay.__str__())
                        normalVector = hit_point_vector.sub(circle.center_vector)
                        normalVector.size = -1
                        angle = acos(normalVector.dot(workingRay.direction))*(-1 if workingRay.direction.dot(normalVector.rotateDeg(90)) > 0 else 1)
                        normalVector.size = 1
                        newRayDirection = normalVector.rotate(angle)
                        if workingRay.bounceCounter+1 <= BOUNCES:
                            if workingRay.originalRay is not None:
                                originalRay = workingRay.originalRay
                            else:
                                originalRay = workingRay
                            newRay = Ray(Vector2(tuple([hit_coord + bounce_dir_component*2 for hit_coord, bounce_dir_component in zip(hit_point, normalVector())])), newRayDirection, workingRay.bounceCounter+1, workingRay.color, originalRay)
                            update_list.append(newRay)
                elif workingRay.length >= MAXIMUM_LENGTH:
                    canvas.delete(workingRay.__str__())
                    #canvas.create_line(workingRay.origin(), [origin+direction*500 for origin, direction in zip(workingRay.origin(), workingRay.direction())], fill="black", tags=workingRay.__str__())
            else: # TODO: Fix issue with bouncing inside a clipping circle
                # TODO: Fix issue where some rays disappear
                intersectionToCenterSize = sqrt(circle.radius**2-rayCenterDistance**2)
                relative_hit = Vector2(tuple([dir_coord*(rayProjection-intersectionToCenterSize) for dir_coord in workingRay.direction()]))
                hit_point = [origin_coord+dir_coord*(rayProjection+intersectionToCenterSize) for origin_coord, dir_coord in zip(workingRay.origin(), workingRay.direction())]
                hit_point_vector = Vector2(tuple(hit_point))
                if relative_hit.size < workingRay.length:
                    if not workingRay.length >= MAXIMUM_LENGTH:
                        update_list.pop()
                    workingRay.length = relative_hit.size
                    workingRay.color = tuple([ray_component*circle_component for ray_component, circle_component in zip(color, circle.color)])
                    canvas.delete(workingRay.__str__())
                    # canvas.create_rectangle(hit_point, hit_point, outline='red',fill='red', tags=workingRay.__str__())
                    canvas.create_line(workingRay.origin(), hit_point, fill=colorToHEX(workingRay.color), tags = workingRay.__str__())
                    normalVector = hit_point_vector.sub(circle.center_vector)
                    normalVector.size = 1
                    # canvas.create_line(hit_point, [coord+component*100 for coord, component in zip(hit_point, normalVector())])
                    angle = acos(normalVector.dot(workingRay.direction))*(-1 if workingRay.direction.dot(normalVector.rotateDeg(90)) > 0 else 1)
                    normalVector.size = -1
                    newRayDirection = normalVector.rotate(angle)
                    if workingRay.bounceCounter+1 < BOUNCES:
                        if workingRay.originalRay is not None:
                            originalRay = workingRay.originalRay
                        else:
                            originalRay = workingRay
                        newRay = Ray(Vector2(tuple([hit_coord + bounce_dir_component*2 for hit_coord, bounce_dir_component in zip(hit_point, normalVector())])), newRayDirection, workingRay.bounceCounter+1, workingRay.color, originalRay)
                        update_list.append(newRay)
                if workingRay.bounceCounter+1 <= BOUNCES:
                    newRay = Ray(Vector2(tuple(hit_point)), Vector2((1,0)), workingRay.bounceCounter+1)
                    update_list.append(newRay)

canvas.mainloop()