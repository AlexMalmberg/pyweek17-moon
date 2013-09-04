import math
import pygame
from OpenGL.GL import *

import mesh

pygame.init()
viewport = (800,600)
windowSurfaceObj = pygame.display.set_mode(viewport, pygame.OPENGL | pygame.DOUBLEBUF)
pygame.display.set_caption('Test the Mesh')

ojb = mesh.ObjMesh('data/model/castle.obj',
                   scale=[0.5,0.5,0.5],offset=[0.0,0.0,0.0])

clock = pygame.time.Clock()

glMatrixMode(GL_PROJECTION)
glLoadIdentity()
glEnable(GL_DEPTH_TEST)
glMatrixMode(GL_MODELVIEW)

while 1:
    clock.tick(60)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()

    ojb.Render(center=[0,0],scale=[0.5,0.5,0.5],forward=[1,1])

    pygame.display.flip()

