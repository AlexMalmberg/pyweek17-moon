import ctypes
import math
import numpy


class Lightmap(object):
  def __init__(self, level, oversample):
    self.level = level
    self.oversample = oversample
    self.width, self.height = level.heightdim
    self.heightmap = numpy.fromstring(level.heightmap, dtype=numpy.uint8)
    self.heightmap.shape = (self.height, self.width)
    self.lightmap = numpy.zeros((self.height, self.width), dtype=numpy.uint8)

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
    self.secondary *= self.oversample
    self.dz = dz / abs(self.primary)
    self.primary = math.copysign(1, self.primary)
    self.progress = 0
    self.partial_ds = 0
    print self.lr, self.primary, self.secondary

  # numpy version
  #
  # clocks in around 300ms per iteration on 2k x 2k, no oversampling
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
