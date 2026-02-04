import tkinter
from typing import Any
from math import sqrt, sin, cos, acos, pi
from random import *

root = tkinter.Tk()

canvas = tkinter.Canvas(width=600, height=600)
canvas.pack()

BOUNCES = 1

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
        return Vector2((vec[0]*cos(angle)-vec[1]*sin(angle),vec[0]*sin(angle)+vec[1]*cos(angle)))
    
    def rotateDeg(self, angle:float):
        angle = angle/360*2*pi
        vec = self()
        return Vector2((vec[0]*cos(angle)-vec[1]*sin(angle),vec[0]*sin(angle)+vec[1]*cos(angle)))
    
    def getAngle(self, vector:'Vector2'):
        vec = self()

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
    
    def __str__(self):
        return f"Ray(({self.origin.size*self.origin.direction[0]}, {self.origin.size*self.origin.direction[1]}), ({self.direction.direction[0]}, {self.direction.direction[1]}))"
    
    def __call__(self):
        return (self.origin, self.direction)

circ = Circle((300,300), 100)

origin = Vector2((100,500))
circ_vec = circ.center_vector.sub(origin)

rays = []

def clickHandler(e, remove=True):
    global rays
    rays = []
    try:
        click = Vector2((e.x, e.y))
    except Exception:
        click = Vector2((e["x"], e["y"]))
    # canvas.create_line(origin(), click(), fill = 'green', tags='line22')
    updateRay(click, remove)

def updateRay(click, remove=True):
    global rays
    dir = click.sub(origin).direction
    rays.append(Ray(origin, Vector2(dir).sub(origin)))
    proj = circ_vec.dot(Vector2(dir))
    d = sqrt(round(circ_vec.size**2-proj**2,10))
    collision = circ.radius-d
    if remove:
        canvas.delete("line2")
        canvas.delete('line22')
    # print(Vector2(dir).dot(circ_vec))
    if collision >=0 and (proj > 0 if Vector2(dir).dot(circ_vec) > 0 else True):
        # print(dir, proj, d)
        t = sqrt(circ.radius**2 - d**2)
        # canvas.create_rectangle(origin()[0]+dir[0]*(proj-t),origin()[1]+dir[1]*(proj-t), origin()[0]+dir[0]*(proj-t),origin()[1]+dir[1]*(proj-t), outline='red')
        if proj-t > 0:
            hit_point = (origin()[0]+dir[0]*(proj-t),origin()[1]+dir[1]*(proj-t))
        else:
            hit_point = (origin()[0]+dir[0]*(proj+t),origin()[1]+dir[1]*(proj+t))
        p_hit = Vector2(hit_point).sub(circ.center_vector)
        p_hit.size = 1
        # canvas.create_line(hit_point[0],hit_point[1], hit_point[0] + p_hit()[0]*100,hit_point[1] + p_hit()[1]*100, fill='blue', tags='line22')
        determining = p_hit.rotateDeg(90)
        angle = acos(round(-p_hit.dot(Vector2(dir)),10)) * (1 if determining.dot(Vector2(dir)) > 0 else -1)# if randint(1,100) < 90 else (randint(int(-pi/2*10000),int(pi/2*10000))/10000)
        bounce = p_hit.rotate(angle)
        # canvas.create_rectangle(origin()[0]+dir[0]*(proj),origin()[1]+dir[1]*proj, origin()[0]+dir[0]*(proj),origin()[1]+dir[1]*proj)
        canvas.create_line(origin(), hit_point[0],hit_point[1], tags = 'line2', fill = 'red')
        canvas.create_line(hit_point[0],hit_point[1], hit_point[0] + bounce()[0]*100,hit_point[1]+bounce()[1]*100, fill='blue', tags='line22')
    else:
        canvas.create_line(origin(), origin()[0]+dir[0]*500,origin()[1]+dir[1]*500, tags = 'line2', fill = 'black')

def redraw(e):
    for i in range(50,550,10):
        clickHandler({"x":300, "y":i}, remove=False)
    canvas.lift('line22')

def moveOrigin(e):
    global origin, circ_vec
    origin = Vector2((e.x, e.y))
    circ_vec = circ.center_vector.sub(origin)
    canvas.delete('line2')
    canvas.delete('line22')
    redraw('')
    # print()

canvas.create_oval(circ(), tags = "circle")

canvas.bind('<Button-1>', clickHandler)
canvas.bind('<B1-Motion>', clickHandler)
canvas.bind_all('<space>', redraw)
canvas.bind('<Button-2>', moveOrigin)
canvas.bind('<B2-Motion>', moveOrigin)

redraw("")

root.mainloop()