import ctypes
import math
import numpy


class Lightmap(object):
  def __init__(self, level, oversample):
    self.level = level
    self.oversample = oversample
    self.width, self.height = level.heightdim
    #self.heightmap = level.heightmap
    self.heightmap = numpy.fromstring(level.heightmap, dtype=numpy.uint8)
    self.heightmap.shape = (self.height, self.width)
    #self.lightmap = (ctypes.c_ubyte * (self.width * self.height))()
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

    #self.dim = self.sdim * self.oversample
    #self.partial = (ctypes.c_float * self.dim)()
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
    if self.lr:
      pmul = 1
      smul = self.width
    else:
      pmul = self.width
      smul = 1
    if self.primary < 0:
      offset = (self.pdim - self.progress - 1) * pmul
    else:
      offset = self.progress * pmul

    fsize = ctypes.sizeof(ctypes.c_float)

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

    # Update partial by subtracting dz and taking max against heightmap.
    # Write partial to lightmap.
    self.partial -= self.dz
    if self.primary > 0:
      o = self.progress
    else:
      o = self.pdim - self.progress - 1
    if self.lr:
      src = self.heightmap.T[o]
    else:
      src = self.heightmap[o]

    numpy.maximum(self.partial, src, self.partial)

    if self.lr:
      self.lightmap.T[o] = self.partial
    else:
      self.lightmap[o] = self.partial

    self.progress += 1

  # 7.964s for 2k x 2k with oversample = 1
  def pre_numpy_CalculateRow(self):
    if self.lr:
      pmul = 1
      smul = self.width
    else:
      pmul = self.width
      smul = 1
    if self.primary < 0:
      offset = (self.pdim - self.progress - 1) * pmul
    else:
      offset = self.progress * pmul

    fsize = ctypes.sizeof(ctypes.c_float)

    # Shift the partial if needed.
    if abs(self.partial_ds) > 1:
      if self.partial_ds > 0:
        ctypes.memmove(ctypes.byref(self.partial, fsize),
                       ctypes.byref(self.partial, 0),
                       fsize * (self.dim - 1))
        self.partial[self.dim - 1] = 0
        self.partial_ds -= 1
      else:
        ctypes.memmove(ctypes.byref(self.partial, 0),
                       ctypes.byref(self.partial, fsize),
                       fsize * (self.dim - 1))
        self.partial[0] = 0
        self.partial_ds += 1
    self.partial_ds += self.secondary

    # Update partial by subtracting dz and taking max against heightmap.
    # Write partial to lightmap.
    j = self.oversample
    s = 0
    for i in xrange(self.dim):
      h = ord(self.heightmap[offset])
      l = max(h, self.partial[i] - self.dz)
      self.partial[i] = l
      s += l
      j -= 1
      if j == 0:
        self.lightmap[offset] = int(s / self.oversample)
        s = 0
        j = self.oversample
        offset += smul

    self.progress += 1

  def UpdateCalculation(self, target_progress):
    target_row = int(target_progress * self.height)
    while self.progress < target_row:
      #print self.progress
      self._CalculateRow()

  def FinishCalculation(self):
    self.UpdateCalculation(1.0)
