import tkinter
from math import sqrt, sin, cos, acos, pi, ceil, floor, copysign
from random import *
from uuid import uuid4
import threading


#=======================#
#   UTILITY FUNCTIONS   #
#=======================#

def clamp(variable, minimum, maximum):
    return min(max(variable, minimum), maximum)

def colorToHEX(color):
    return f"#{clamp(int(color[0]*255),0,255):02x}{clamp(int(color[1]*255),0,255):02x}{clamp(int(color[2]*255),0,255):02x}"

def closeFactors(number:int):
    factor = floor(sqrt(number))
    while number//factor != number/factor:
        factor -= 1
    return (factor, number//factor)


#=======================#
#   CLASS DEFINITIONS   #
#=======================#

class Sphere:
    def __init__(self, center: tuple[float, float, float], radius, color: tuple[float, float, float]=(1,1,1), light_source: bool = False, scattering:float = 0):
        self.center_x = center[0]
        self.center_y = center[1]
        self.center_z = center[2]
        self.radius = radius
        self.center_vector = Vector(center)
        self.color = color
        self.light_source = light_source
        self.scatteringCoefficient = clamp(scattering, 0, 1)

    def __call__(self):
        return ((self.center_x-self.radius,self.center_y-self.radius,self.center_z-self.radius),(self.center_x+self.radius,self.center_y+self.radius,self.center_z+self.radius))

class Vector2:
    def __init__(self, vector:tuple[float, float]):
        self.size = sqrt(vector[0]**2+vector[1]**2)
        try:
            self.direction = (vector[0]/self.size, vector[1]/self.size)
        except Exception:
            self.direction = (0,0)
    
    def dot(self, vector:'Vector2'):
        return self.size*vector.size*(self.direction[0]*vector.direction[0]+self.direction[1]*vector.direction[1])
    
    def add(self, vector:'Vector2'):
        return Vector2((self.size*self.direction[0]+vector.size*vector.direction[0],self.size*self.direction[1]+vector.size*vector.direction[1]))
    
    def sub(self, vector:'Vector2'):
        return Vector2((self.size*self.direction[0]-vector.size*vector.direction[0],self.size*self.direction[1]-vector.size*vector.direction[1]))
    
    def mul(self, scalar:float):
        vec = self()
        return Vector2((vec[0]*scalar,vec[1]*scalar))
    
    def rotate(self, angle:float):
        vec = self()
        angle *= -1
        return Vector2((vec[0]*cos(angle)-vec[1]*sin(angle),vec[0]*sin(angle)+vec[1]*cos(angle)))
    
    def rotateDeg(self, angle:float):
        angle = -angle/360*2*pi
        vec = self()
        return Vector2((vec[0]*cos(angle)-vec[1]*sin(angle),vec[0]*sin(angle)+vec[1]*cos(angle)))

    def __str__(self):
        return f"Vector2({self.size*self.direction[0]}, {self.size*self.direction[1]})"
    
    def __call__(self):
        return (self.size*self.direction[0], self.size*self.direction[1])

class Vector:
    def __init__(self, vector:tuple[float, float, float]):
        self.size = sqrt(vector[0]**2+vector[1]**2+vector[2]**2)
        try:
            self.direction = (vector[0]/self.size, vector[1]/self.size, vector[2]/self.size)
        except Exception:
            self.direction = (0,0,0)
    
    def dot(self, vector:'Vector'):
        return self.size*vector.size*(self.direction[0]*vector.direction[0]+self.direction[1]*vector.direction[1]+self.direction[2]*vector.direction[2])
    
    def dot2(self, vector:'Vector', idx_offset:int):
        return self.size*vector.size*(self.direction[(0+idx_offset)%3]*vector.direction[(0+idx_offset)%3]+self.direction[(1+idx_offset)%3]*vector.direction[(1+idx_offset)%3])

    def unitDot2(self, vector:'Vector', idx_offset:int):
        a = Vector2((self.direction[(0+idx_offset)%3], self.direction[(1+idx_offset)%3]))
        b = Vector2((vector.direction[(0+idx_offset)%3], vector.direction[(1+idx_offset)%3]))
        a.size = 1
        b.size = 1
        return a.dot(b)

    def add(self, vector:'Vector'):
        return Vector((self.size*self.direction[0]+vector.size*vector.direction[0],self.size*self.direction[1]+vector.size*vector.direction[1],self.size*self.direction[2]+vector.size*vector.direction[2]))
    
    def sub(self, vector:'Vector'):
        return Vector((self.size*self.direction[0]-vector.size*vector.direction[0],self.size*self.direction[1]-vector.size*vector.direction[1],self.size*self.direction[2]-vector.size*vector.direction[2]))
    
    def mul(self, scalar:float):
        vec = self()
        return Vector((vec[0]*scalar,vec[1]*scalar,vec[2]*scalar))
    
    def rotate(self, angle_z:float, angle_y:float):
        vec = self()
        angle_z *= 1
        angle_y *= 1
        vec  = Vector((vec[0]*cos(angle_z)-vec[1]*sin(angle_z),vec[0]*sin(angle_z)+vec[1]*cos(angle_z),vec[2]))()
        return Vector((vec[0]*cos(angle_y)+vec[2]*sin(angle_y),vec[1],vec[2]*cos(angle_y)-vec[0]*sin(angle_y)))
    
    def rotateDeg(self, angle_z:float, angle_y:float):
        angle_z = angle_z/360*2*pi
        angle_y = angle_y/360*2*pi
        return self.rotate(angle_z, angle_y)

    def normalizedVector2(self, idx_offset:int):
        a=Vector2((self.direction[(0+idx_offset)%3], self.direction[(1+idx_offset)%3]))
        a.size = 1
        return a

    def __str__(self):
        return f"({self.size*self.direction[0]}, {self.size*self.direction[1]}, {self.size*self.direction[2]})"
    
    def __call__(self):
        return (self.size*self.direction[0], self.size*self.direction[1], self.size*self.direction[2])

class Ray:
    def __init__(self, origin:'Vector', direction:'Vector', bounceCounter:int = 0, color:tuple[float, float, float] = (1,1,1), originalRay:'Ray'=None):
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
    
    def rot(self, angle_z:float, angle_y:float):
        # Rotate by radians
        self.direction = self.direction.rotate(angle_z, angle_y)

    def rotDeg(self, angle_z:float, angle_y:float):
        # Rotate by degrees
        self.direction = self.direction.rotateDeg(angle_z, angle_y)

    def setLightHit(self, hit:bool):
        self.hit_light = hit
        if self.originalRay is not None:
            self.originalRay.setLightHit(hit)
    
    def updateColors(self):
        if self.childRay is not None:
            self.childRay.updateColors()
            self.color = tuple([a*b for a,b in zip(self.childRay.color, self.bounceColor)])
        else:
            self.color = self.bounceColor

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


# Source - https://stackoverflow.com/a/6894023
# Posted by kindall, modified by community. See post 'Timeline' for change history
# Retrieved 2026-02-14, License - CC BY-SA 4.0

class ThreadWithReturnValue(threading.Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        threading.Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        threading.Thread.join(self, *args)
        return self._return


#==============================#
#   CONFIGURATION PARAMETERS   #
#==============================#

FOV = 60
ROTATION = 0
BOUNCES = 40
MAXIMUM_LENGTH = 100000000
RESOLUTION = 5
RAYS_PER_PX = 200

THREADS = 50
RAY_GROUPS = 100

ray_origin = Vector((400, 300, 0))
circles = [
    # forward/back, side/side, up/down
    Sphere((-200,300,0), 590, color = (1,1,1), light_source=True),
    Sphere((600,300,0), 25, color = (1,1,1), scattering=0.85),
    Sphere((600,100,0), 150, color = (1,0.2,0.2), scattering=0.15),
    Sphere((600,500,0), 150, color = (0.2,0.2,1), scattering=0.15)
]

smoothingMatrix = {
    -2*(600//RESOLUTION)-2: 0.0, -2*(600//RESOLUTION)-1: 0.05, -2*(600//RESOLUTION): 0.1, -2*(600//RESOLUTION)+1: 0.05,-2*(600//RESOLUTION)+2:  0.0,
    -(600//RESOLUTION) - 2: 0.05, -(600//RESOLUTION) - 1: 0.1, -(600//RESOLUTION)  : 0.2, -(600//RESOLUTION) + 1: 0.1, -(600//RESOLUTION) +2:  0.05,
    -2                    : 0.1, -1                    : 0.2, 0                   : 1  , 1                     : 0.2, 2                    :  0.1, 
    (600//RESOLUTION) - 2 : 0.05, (600//RESOLUTION)-1.  : 0.1, (600//RESOLUTION)   : 0.2, (600//RESOLUTION) + 1 : 0.1,  (600//RESOLUTION) +2:  0.05,
    2*(600//RESOLUTION) -2: 0.0, 2*(600//RESOLUTION)-1 : 0.05, 2*(600//RESOLUTION) : 0.1, 2*(600//RESOLUTION) +1: 0.05, 2*(600//RESOLUTION)+2:  0.0
}

root = tkinter.Tk()

canvas = tkinter.Canvas(width=600,height=600)
canvas.grid(column=0,row=0)

def calculateRay(workingRay:'Ray', bounces:int, DEBUG: bool = False):
    hit_light_source = False
    returning_ray = None
    normalVector = None
    relevantSphere = None
    for circle in circles:
        vectorToCircleCenter = circle.center_vector.sub(workingRay.origin)
        if vectorToCircleCenter.size >= circle.radius:
            rayProjection = workingRay.direction.dot(vectorToCircleCenter)
            try:
                rayCenterDistance = sqrt(vectorToCircleCenter.size**2-rayProjection**2)
            except Exception:
                rayCenterDistance = 0
            if circle.radius - rayCenterDistance > 0 and rayProjection > 0:
                intersectionToCenterSize = sqrt(circle.radius**2-rayCenterDistance**2)
                relative_hit = Vector(tuple([dir_coord*(rayProjection-intersectionToCenterSize) for dir_coord in workingRay.direction()]))
                hit_point = [origin_coord+dir_coord*(rayProjection-intersectionToCenterSize) for origin_coord, dir_coord in zip(workingRay.origin(), workingRay.direction())]
                hit_point_vector = Vector(tuple(hit_point))
                if relative_hit.size < workingRay.length:
                    if hit_light_source:
                        workingRay.setLightHit(False)
                        hit_light_source = False
                    relevantSphere = circle
                    workingRay.length = relative_hit.size
                    workingRay.bounceColor = tuple([circle_component for circle_component in circle.color])
                    workingRay.end = hit_point_vector
                    normalVector = hit_point_vector.sub(circle.center_vector)
                    normalVector.size = 1
                    scatter_coefficient = randrange(0,10000)/10000
                    if scatter_coefficient < circle.scatteringCoefficient:
                        angle_z = randrange(int(-pi/2*10000),int(pi/2*10000))/10000
                        angle_y = randrange(int(-pi/2*10000),int(pi/2*10000))/10000
                        newRayDirection = normalVector.rotate(angle_z,angle_y)
                    else:
                        newRayDirection = workingRay.direction.sub(normalVector.mul(2*normalVector.dot(workingRay.direction)))
                        #angle_z = acos(clamp(normalVector.unitDot2(workingRay.direction,0),-1,1))*copysign(1, normalVector.unitDot2(workingRay.direction.rotateDeg(-90,0),0))
                        #angle_y = acos(clamp(normalVector.unitDot2(workingRay.direction,2),-1,1))*(-1 if normalVector.unitDot2(workingRay.direction.rotateDeg(0,90),2) > 0 else 1)
                    if circle.light_source:
                        hit_light_source = True
                        workingRay.setLightHit(True)
                        workingRay.color = circle.color
                    elif workingRay.bounceCounter+1 <= bounces:
                        if workingRay.originalRay is not None:
                            originalRay = workingRay
                        else:
                            originalRay = workingRay
                        newRay = Ray(Vector(tuple([hit_coord + 2*bounce_dir_component for hit_coord, bounce_dir_component in zip(hit_point, normalVector())])), newRayDirection, workingRay.bounceCounter+1, originalRay=workingRay)
                        returning_ray = newRay
                        workingRay.childRay = newRay
        else: # TODO: Fix issue with bouncing inside a clipping circle
            # TODO: Fix issue where some rays disappear
            try:
                intersectionToCenterSize = sqrt(circle.radius**2-rayCenterDistance**2)
                relative_hit = Vector(tuple([dir_coord*(rayProjection-intersectionToCenterSize) for dir_coord in workingRay.direction()]))
                hit_point = [origin_coord+dir_coord*(rayProjection+intersectionToCenterSize) for origin_coord, dir_coord in zip(workingRay.origin(), workingRay.direction())]
                hit_point_vector = Vector(tuple(hit_point))
                if relative_hit.size < workingRay.length:
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
                    if workingRay.bounceCounter+1 < bounces:
                        if workingRay.originalRay is not None:
                            originalRay = workingRay.originalRay
                        else:
                            originalRay = workingRay
                        newRay = Ray(Vector2(tuple([hit_coord + bounce_dir_component*2 for hit_coord, bounce_dir_component in zip(hit_point, normalVector())])), newRayDirection, workingRay.bounceCounter+1, workingRay.color, originalRay)
                        update_list.append(newRay)
                    if workingRay.bounceCounter+1 <= bounces:
                        newRay = Ray(Vector2(tuple(hit_point)), Vector2((1,0)), workingRay.bounceCounter+1)
                        update_list.append(newRay)
            except Exception:
                continue
    if not DEBUG:
        return returning_ray
    else:
        return normalVector, relevantSphere

def threadGroup(workingRayGroup, bounces, DEBUG=False):
    temp = []
    for ray in workingRayGroup:
        new = calculateRay(ray, bounces, DEBUG)
        if new is not None:
            temp.append(new)
    return temp

angle_per_pixel = FOV/(600/RESOLUTION)
factors = closeFactors(RAYS_PER_PX)
angle_per_ray_x = angle_per_pixel/factors[0]
angle_per_ray_y = angle_per_pixel/factors[1]


pixel_list: list[list['Ray']] = [[] for _ in range(int(600//RESOLUTION)**2)]

def render(fov, resolution, rays_per_px, bounces, ray_id):
    global pixel_list
    update_list: list['Ray'] = []

    x_ray = ray_id%factors[1]
    y_ray = ray_id//factors[1]
    # print(x_ray, y_ray)
    for x in range(0,600,resolution):
        for y in range(0,600,resolution):
            angle_z = (y/resolution-1)*angle_per_pixel+angle_per_ray_y*y_ray-fov/2
            angle_y = (x/resolution-1)*angle_per_pixel+angle_per_ray_x*x_ray-fov/2
            ray = Ray(origin=ray_origin, direction=Vector((1, 0, 0)))
            ray.rotDeg(angle_z, angle_y+ROTATION)
            update_list.append(ray)
            pixel_list[int(y//resolution)+int((600//resolution)*(x//resolution))].append(ray)

    threads: list[threading.Thread] = []
    for _ in range(THREADS):
        thread = ThreadWithReturnValue(target=threadGroup, args = (update_list[max(0,len(update_list)-RAY_GROUPS):len(update_list)], bounces))
        del update_list[max(0,len(update_list)-RAY_GROUPS):len(update_list)]
        thread.start()
        threads.append(thread)

    while True:
        for i, thread in enumerate(threads):
            if not thread.is_alive():
                newRays = thread.join()
                if newRays is not []:
                    update_list+=newRays
                threads.pop(i)
                if update_list != []:
                    thread = ThreadWithReturnValue(target=threadGroup, args = (update_list[max(0,len(update_list)-RAY_GROUPS):len(update_list)], bounces))
                    del update_list[max(0,len(update_list)-RAY_GROUPS):len(update_list)]
                    thread.start()
                    threads.append(thread)
        if threads == []:
            break

    rawColorMap = []
    for ray_list in pixel_list:
        # print(len(pixel_list))
        #if ray.hit_light:
            #ray.drawRay(canvas2)
        color = (0,0,0)
        for ray in ray_list:
            ray.updateColors()
            color = [(component+ray_color if ray.hit_light else component) for component, ray_color in zip(color, ray.color)]
        color = tuple([clamp(component/(ray_id+1)*1.05,0,1) for component in color])
        rawColorMap.append(color)

    # colorMap = []
    # for i in range(len(rawColorMap)):
    #     color = (0,0,0)
    #     sum_smoothing_matrix = sum(smoothingMatrix.values())
    #     for pos, filter in smoothingMatrix.items():
    #         color = [color_comp+filter*new_comp/sum_smoothing_matrix for color_comp, new_comp in zip(color, rawColorMap[int(i+pos)%len(rawColorMap)])]
    #     color = tuple(color)
    #     colorMap.append(color)
    # rawColorMap = colorMap.copy()
    # colorMap = []
    # for i in range(len(rawColorMap)):
    #     color = (0,0,0)
    #     for pos, filter in smoothingMatrix.items():
    #         color = [color_comp+filter*new_comp/sum_smoothing_matrix for color_comp, new_comp in zip(color, rawColorMap[int(i+pos)%len(rawColorMap)])]
    #     colorMap.append(color)
    colorMap = rawColorMap

    canvas.delete('all')
    for i, color in enumerate(colorMap):
        x = i%(600//resolution)
        y = i//(600//resolution)
        canvas.create_rectangle((x)*resolution, (y)*resolution, (x+1)*resolution, (y+1)*resolution, fill = colorToHEX(color), outline="")
    canvas.update()
    if ray_id < RAYS_PER_PX:
        canvas.after('idle', render, fov, resolution, rays_per_px, bounces, ray_id+1)
    else:
        print("DONE")

def start():
    render(FOV, RESOLUTION, 200, BOUNCES, 0)

def clickHandler(e):
    coord = (e.x, e.y)
    angles = ((coord[0]/RESOLUTION-1)*angle_per_pixel-FOV/2,(coord[1]/RESOLUTION-1)*angle_per_pixel-FOV/2)
    ray = Ray(origin=ray_origin, direction=Vector((1, 0, 0)))
    ray.rotDeg(angles[0], angles[1]+ROTATION)
    normal, sphere = calculateRay(ray, 0, DEBUG=True)
    #print(f'a={ray.end()}')
    print(f'{normal()}')
    #print(sphere())
    print(f'{ray.direction()}')
    print(ray.direction.sub(normal.mul(2*normal.dot(ray.direction))))
    #print(f'd={sphere.center_vector()}')

# canvas.after_idle(render, FOV, RESOLUTION, 1, 1)
button = tkinter.Button(text="Render",command=start)
button.grid(row=1,column=0)

canvas.bind('<Button-1>',clickHandler)

root.mainloop()