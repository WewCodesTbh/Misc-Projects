from turtle import *
import random
import math
import time

COLOURS = [(0,0,1), (0.1, 0.1, 0.1)]
setworldcoordinates(0, 0, 1000, 1000)
bgcolor((0,0,0))

BINDING_ENERGY = -1 #should be negative, determines the "boiling point" of the simulation, lower it is the higher the boiling point
DENSITY = 1 #larger -> more empty space in simulation

def gen_grid(n, screen_size = [1000, 1000]):
    T = []
    scale = [screen_size[0]*0.6/n, screen_size[1]*0.6/n]
    for i in range(n):
        row = []
        data_row = []
        for j in range(n):
            t = Turtle()
            t.shape("square")
            t.pu()
            t.goto(screen_size[0]*0.2+scale[0]*i, screen_size[1]*0.2+scale[1]*j)
            x = min(random.randint(0,DENSITY), 1)
            t.color(COLOURS[x])
            row.append(t)
        T.append(row)
    return T

def neighbour_total(T, i, j):
    s = 0
    for a in range(-1, 2):
        for b in range(-1, 2):
            try:
                if sum([i for i in T[i+a][j+b].color()[0]]) > 0.5 and (a, b) != (0,0):
                    s -= BINDING_ENERGY
            except IndexError:
                pass
    return s

def swap(T, t):
    i1, j1 = random.randint(0, len(T)-1), random.randint(0, len(T[0])-1)
    i2, j2 = random.randint(0, len(T)-1), random.randint(0, len(T[0])-1)
    X, Y = sum([i for i in T[i1][j1].color()[0]]), sum([i for i in T[i2][j2].color()[0]])
    if (X > 0.7 and Y < 0.5):
            N1, N2 = neighbour_total(T, i1, j1), neighbour_total(T, i2, j2)
            try:
                deltaE = math.exp((N1-N2)/t)
                prob = deltaE/(1+deltaE)
            except OverflowError:
                prob = 1
            #print(N1, N2, deltaE, prob, t)
            if random.random() <= prob:
                store = T[i1][j1].color()[0]
                T[i1][j1].color(T[i2][j2].color()[0])
                T[i2][j2].color(store)

tracer(100, 0)
delay(0)
T= gen_grid(20)
tracer(1, 0)
temperature = float(input("tempreature: "))
step = 0
t = time.time()
while True:
    swap(T, temperature)
    if step%1000 == 0:
        entropy = sum([sum([neighbour_total(T, i, j) for i in range(len(T))]) for j in range(len(T))])
        print(-entropy/len(T)**2, step, time.time()-t)
        t = time.time()
    step += 1
