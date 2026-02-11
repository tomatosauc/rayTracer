import tkinter
from math import sqrt, sin, cos, acos, pi
from random import *
from uuid import uuid4


#=======================#
#   UTILITY FUNCTIONS   #
#=======================#

def clamp(variable, minimum, maximum):
    return min(max(variable, minimum), maximum)

def colorToHEX(color):
    return f"#{int(color[0]*255):02x}{int(color[1]*255):02x}{int(color[2]*255):02x}"


#=======================#
#   CLASS DEFINITIONS   #
#=======================#

class Circle:
    def __init__(self, center: tuple[float, float], radius, color: tuple[float, float, float]=(1,1,1), light_source: bool = False, scattering:float = 0):
        self.center_x = center[0]
        self.center_y = center[1]
        self.radius = radius
        self.center_vector = Vector2(center)
        self.color = color
        self.light_source = light_source
        self.scatteringCoefficient = clamp(scattering, 0, 1)

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
        self.end = None
        self.hit_light = False
        self.bounceColor = (0,0,0)
        self.childRay = None
    
    def rot(self, angle:float):
        # Rotate by radians
        self.direction = self.direction.rotate(angle)

    def rotDeg(self, angle:float):
        # Rotate by degrees
        self.direction = self.direction.rotateDeg(angle)
    
    def setLightHit(self, hit:bool):
        self.hit_light = hit
        if self.originalRay is not None:
            self.originalRay.setLightHit(hit)

    def drawRay(self, canvas:tkinter.Canvas):
        if self.end is not None:
            if self.childRay is not None:
                self.childRay.drawRay(canvas)
                self.color = tuple([a*b for a,b in zip(self.childRay.color, self.bounceColor)])
            canvas.create_line(self.origin(), self.end(), fill = colorToHEX(self.color))

    def __str__(self):
        return f"Ray({self.id})"
    
    def __call__(self):
        return (self.origin, self.direction)


#==============================#
#   CONFIGURATION PARAMETERS   #
#==============================#

FOV = 120
ROTATION = 0
# NUM_OF_RAYS = 2000
BOUNCES = 100
MAXIMUM_LENGTH = 100000000
RESOLUTION = 2
RAYS_PER_PX = 100

angle_per_resolution_per_ray = FOV/(600/RESOLUTION)/RAYS_PER_PX


canvas = tkinter.Canvas(width=600,height=600)
canvas.pack()

ray_origin = Vector2((300, 300))

"""circles = [
    Circle((randrange(0,400), randrange(0,600)), randrange(50,100), color=(clamp(randrange(100,1500),0,1000)/1000,clamp(randrange(100,1500),0,1000)/1000,clamp(randrange(100,1500),0,1000)/1000), scattering= clamp(randrange(-1000,10000), 0, 0)/10000, light_source=choice((False, False, False, False, True)))
    for _ in range(10)
]"""

circles = [
    Circle((0,300), 200, color = (1,1,1), light_source=True),
    Circle((750, 300), 200, color = (0.2,1,0.2)),
    Circle((600,0), 200, color = (1,0.2,0.2)),
    Circle((600, 600), 200, color = (0.2,0.2,1))
]

update_list: list['Ray'] = []
original_ray_list: list['Ray'] = []

#for angle in range(int((ROTATION-FOV/2)*100), int((ROTATION+FOV/2+1)*100), int(FOV/NUM_OF_RAYS*100)):
#    angle/=100
#    ray = Ray(origin=ray_origin, direction=Vector2((1,0)))
#    ray.rotDeg(angle)
#   update_list.append(ray)

ray_list = update_list.copy()

#for circle in circles:
#    canvas.create_oval(circle(),outline=colorToHEX(circle.color))

#for ray in ray_list:
#    if ray.hit_light and ray.end is not None:
#        ray.drawRay(canvas)

canvas2 = tkinter.Canvas(width=600, height=600)
canvas2.pack()

for y in range(0,600,RESOLUTION):
    for ray_id in range(RAYS_PER_PX):
        angle = (ray_id+y/RESOLUTION*RAYS_PER_PX+1)*angle_per_resolution_per_ray-FOV/2
        ray = Ray(origin=ray_origin, direction=Vector2((1, 0)))
        ray.rotDeg(angle+ROTATION)
        # print(ray.direction)
        update_list.append(ray)
        ray_list.append(ray)

while True:
    if update_list == []:
        break
    else:
        hit_light_source = False
        workingRay = update_list.pop(0)
        for circle in circles:
            vectorToCircleCenter = circle.center_vector.sub(workingRay.origin)
            if vectorToCircleCenter.size >= circle.radius:
                rayProjection = workingRay.direction.dot(vectorToCircleCenter)
                try:
                    rayCenterDistance = sqrt(round(vectorToCircleCenter.size**2-rayProjection**2,5))
                except Exception:
                    rayCenterDistance = 0
                if circle.radius - rayCenterDistance > 0 and rayProjection > 0:
                    intersectionToCenterSize = sqrt(circle.radius**2-rayCenterDistance**2)
                    relative_hit = Vector2(tuple([dir_coord*(rayProjection-intersectionToCenterSize) for dir_coord in workingRay.direction()]))
                    hit_point = [origin_coord+dir_coord*(rayProjection-intersectionToCenterSize) for origin_coord, dir_coord in zip(workingRay.origin(), workingRay.direction())]
                    hit_point_vector = Vector2(tuple(hit_point))
                    if relative_hit.size < workingRay.length:
                        if not workingRay.length >= MAXIMUM_LENGTH and not hit_light_source:
                            update_list.pop()
                        else:
                            workingRay.setLightHit(False)
                            hit_light_source = False
                        workingRay.length = relative_hit.size
                        workingRay.bounceColor = tuple([circle_component for circle_component in circle.color])
                        workingRay.end = hit_point_vector
                        workingRay.color = (1,1,1)
                        # canvas.delete(workingRay.__str__())
                        # canvas.create_rectangle(hit_point, hit_point, outline='red',fill='red', tags=workingRay.__str__())
                        # canvas.create_line(workingRay.origin(), hit_point, fill=colorToHEX(workingRay.color), tags=workingRay.__str__())
                        normalVector = hit_point_vector.sub(circle.center_vector)
                        normalVector.size = -1
                        scatter_coefficient = randrange(0,10000)/10000
                        if scatter_coefficient < circle.scatteringCoefficient:
                            angle = randrange(int(-pi/2*10000),int(pi/2*10000))/10000
                        else:
                            angle = acos(normalVector.dot(workingRay.direction))*(-1 if workingRay.direction.dot(normalVector.rotateDeg(90)) > 0 else 1)
                        normalVector.size = 1
                        newRayDirection = normalVector.rotate(angle)
                        if circle.light_source:
                            hit_light_source = True
                            workingRay.setLightHit(True)
                            workingRay.color = circle.color
                        elif workingRay.bounceCounter+1 <= BOUNCES:
                            if workingRay.originalRay is not None:
                                originalRay = workingRay
                            else:
                                originalRay = workingRay
                            newRay = Ray(Vector2(tuple([hit_coord + bounce_dir_component for hit_coord, bounce_dir_component in zip(hit_point, normalVector())])), newRayDirection, workingRay.bounceCounter+1, originalRay=workingRay)
                            update_list.append(newRay)
                            workingRay.childRay = newRay
                # elif workingRay.length >= MAXIMUM_LENGTH:
                    # canvas.delete(workingRay.__str__())
                    # canvas.create_line(workingRay.origin(), [origin+direction*500 for origin, direction in zip(workingRay.origin(), workingRay.direction())], fill="black", tags=workingRay.__str__())
            else: # TODO: Fix issue with bouncing inside a clipping circle
                # TODO: Fix issue where some rays disappear
                try:
                    intersectionToCenterSize = sqrt(circle.radius**2-rayCenterDistance**2)
                    relative_hit = Vector2(tuple([dir_coord*(rayProjection-intersectionToCenterSize) for dir_coord in workingRay.direction()]))
                    hit_point = [origin_coord+dir_coord*(rayProjection+intersectionToCenterSize) for origin_coord, dir_coord in zip(workingRay.origin(), workingRay.direction())]
                    hit_point_vector = Vector2(tuple(hit_point))
                    if relative_hit.size < workingRay.length:
                        if not workingRay.length >= MAXIMUM_LENGTH and not hit_light_source:
                            update_list.pop()
                        workingRay.length = relative_hit.size
                        continue
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
                except Exception:
                    continue

for circle in circles:
    canvas2.create_oval(circle(), outline = colorToHEX(circle.color), fill = colorToHEX(circle.color) if circle.light_source else "")

color = (0,0,0)
for i, ray in enumerate(ray_list):
    if ray.hit_light:
        ray.drawRay(canvas2)
    if i%RAYS_PER_PX == RAYS_PER_PX-1:
        color = tuple([clamp(component/RAYS_PER_PX*1,0,1) for component in color])
        # print(color)
        canvas.create_rectangle(0, (i/RAYS_PER_PX-1)*RESOLUTION, 600, ((i/RAYS_PER_PX)*RESOLUTION), fill = colorToHEX(color) if ray.hit_light else "#000000", outline="")
        color = (0,0,0)
    else:
        color = tuple([(component+ray_color if ray.hit_light else component) for component, ray_color in zip(color, ray.color)])

canvas2.mainloop()
canvas.mainloop()