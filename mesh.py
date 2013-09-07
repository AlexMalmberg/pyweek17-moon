import math
import pygame
from OpenGL.GL import *


class Mesh(object):
  def __init__(self, path):
    vertices = map(float, file(path + '.vert').read().split())
    indices = map(int, file(path + '.idx').read().split())

    self.vbo, self.ibo, self.vnbo = glGenBuffers(3)

    vbuf = (ctypes.c_float * len(vertices))()
    vbuf[:] = vertices[:]

    ibuf = (ctypes.c_uint * len(indices))()
    ibuf[:] = indices[:]

    glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
    glBufferData(GL_ARRAY_BUFFER, ctypes.sizeof(vbuf), vbuf, GL_STATIC_DRAW)
    glBindBuffer(GL_ARRAY_BUFFER, 0)

    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)
    glBufferData(GL_ELEMENT_ARRAY_BUFFER, ctypes.sizeof(ibuf), ibuf,
                 GL_STATIC_DRAW)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    self.num_idx = len(indices)

  def Render(self, center, scale, angle):
    F = ctypes.sizeof(ctypes.c_float)
    FP = lambda x: ctypes.cast(x * F, ctypes.POINTER(ctypes.c_float))

    glBindBuffer(GL_ARRAY_BUFFER, self.vbo)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, self.ibo)

    glEnableClientState(GL_VERTEX_ARRAY)
    glEnableClientState(GL_NORMAL_ARRAY)
    glEnableClientState(GL_TEXTURE_COORD_ARRAY)

    glVertexPointer(3, GL_FLOAT, 8 * F, FP(0))
    glNormalPointer(GL_FLOAT, 8 * F, FP(3))
    glTexCoordPointer(2, GL_FLOAT, 8 * F, FP(6))

    glEnable(GL_NORMALIZE)

    glPushMatrix()
    glTranslate(center[0], center[1], center[2])
    glRotate(angle, 0, 0, 1)
    glScale(scale[0], scale[1], scale[2])
    glEnable(GL_CULL_FACE)
    glCullFace(GL_BACK)
    glDrawElements(GL_TRIANGLES, self.num_idx, GL_UNSIGNED_INT, None)
    glPopMatrix()

    glPolygonMode(GL_FRONT_AND_BACK, GL_FILL)

    glBindBuffer(GL_ARRAY_BUFFER, 0)
    glBindBuffer(GL_ELEMENT_ARRAY_BUFFER, 0)

    glDisable(GL_NORMALIZE)
    glDisable(GL_CULL_FACE)

    glDisableClientState(GL_VERTEX_ARRAY)
    glDisableClientState(GL_NORMAL_ARRAY)
    glDisableClientState(GL_TEXTURE_COORD_ARRAY)
