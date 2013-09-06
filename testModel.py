import math, sys
import pygame
from OpenGL.GL import *

import mesh

pygame.init()
viewport = (800,600)
windowSurfaceObj = pygame.display.set_mode(viewport, pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption('Test the Mesh')

background = pygame.Surface(windowSurfaceObj.get_size())
background = background.convert()
background.fill((250, 250, 250))

scale = [0.2, 0.2, 0.2, 0.2]
offset = [1.0, 1.0, 1.0]

ojb = mesh.ObjMesh('data/model/castle2.obj',
                   scale,offset)

clock = pygame.time.Clock()

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)

x = 0
y = 0
z = 0

while 1:
    clock.tick(60)
    glClearColor(1.0, 1.0, 1.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
        if event.type == pygame.KEYDOWN and event.key == pygame.K_w:
            x += 1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_e:
            x -= 1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_a:
            y += 1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
            y -= 1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_q:
            z += 1
        if event.type == pygame.KEYDOWN and event.key == pygame.K_t:
            z -= 1
            

    ojb.Render(center=[x,y,z],scale=[0.2,0.2,0.2,0.2],forward=[1.5,0.5])
    pygame.display.flip()

