import ctypes
import math
import numpy
from OpenGL.GL import *


class Lightmap(object):
  def __init__(self, level, texture_id):
    self.width, self.height = level.heightdim
    self.heightmap = numpy.fromstring(level.heightmap, dtype=numpy.uint8)
    self.heightmap.shape = (self.height, self.width)
    self.lightmap = numpy.zeros((self.height, self.width), dtype=numpy.uint8)

    self.id = texture_id
    glBindTexture(GL_TEXTURE_2D, self.id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)

  def StartCalculation(self, dx, dy, dz):
    if abs(dx) > abs(dy):
      self.lr = True
      self.primary = dx
      self.secondary = dy
      self.pdim = self.width
      self.sdim = self.height
    else:
      self.lr = False
      self.primary = dy
      self.secondary = dx
      self.pdim = self.height
      self.sdim = self.width

    self.dim = self.sdim
    self.partial = numpy.zeros((self.dim, ))

    self.secondary /= abs(self.primary)
    self.dz = dz / abs(self.primary)
    self.primary = math.copysign(1, self.primary)
    self.progress = 0
    self.partial_ds = 0

  # clocks in around 300ms per iteration on 2k x 2k, no oversampling
  # TODO(alex): try to shift this to the gpu
  # TODO(alex): work out why transposing makes for such a harsh
  # performance hit
  # TODO(alex): work out how to combine oversampling with the numpy
  # implementation
  def _CalculateRow(self):
    if abs(self.partial_ds) > 1:
      if self.partial_ds > 0:
        self.partial[1:] = self.partial[:-1]
        self.partial[0] = 0
        self.partial_ds -= 1
      else:
        self.partial[:-1] = self.partial[1:]
        self.partial[self.dim - 1] = 0
        self.partial_ds += 1
    self.partial_ds += self.secondary

    if self.primary > 0:
      o = self.progress
    else:
      o = self.pdim - self.progress - 1

    # Update partial by subtracting dz...
    self.partial -= self.dz

    # ... and taking max against heightmap.
    if self.lr:
      src = self.heightmap.T[o]
    else:
      src = self.heightmap[o]
    numpy.maximum(self.partial, src, self.partial)

    # Write partial to lightmap.
    if self.lr:
      self.lightmap.T[o] = self.partial
    else:
      self.lightmap[o] = self.partial

    self.progress += 1

  def UpdateCalculation(self, target_progress):
    target_row = int(target_progress * self.height)
    while self.progress < target_row:
      self._CalculateRow()

  def FinishCalculation(self):
    self.UpdateCalculation(1.0)
    glBindTexture(GL_TEXTURE_2D, self.id)
    glTexImage2D(
      GL_TEXTURE_2D, 0, GL_ALPHA, self.width, self.height,
      0, GL_ALPHA, GL_UNSIGNED_BYTE,
      self.lightmap.ctypes.data_as(ctypes.POINTER(ctypes.c_uint8)))
