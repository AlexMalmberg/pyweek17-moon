import math
import numpy
import pygame


class Level(object):
  def __init__(self, path):
    surface = pygame.image.load(path + '/height2.png')
    raw_heightmap = pygame.image.tostring(surface, 'P', 1)
    self.heightmap = numpy.fromstring(raw_heightmap, dtype=numpy.uint8)
    self.heightmap.shape = (surface.get_height(), surface.get_width())

    # TODO(alex): separate collision map
    # TODO(alex): or just build a coarse bsp tree of the geometry?
    self.collisionmap = self.heightmap
    self.collisionscale = [0.5, 0.5]

    # texture(s)

  def Render(self):
    pass

  def CollisionMap(self, x, y):
    if x < 0 or y < 0:
      return True
    if x >= self.collisionmap.shape[1] or y >= self.collisionmap.shape[0]:
      return True
    return bool(self.collisionmap[y][x])

  def Move(self, p, v):
    p = p[:]
    p[0] *= self.collisionscale[0]
    p[1] *= self.collisionscale[1]
    v = v[:]
    v[0] *= self.collisionscale[0]
    v[1] *= self.collisionscale[1]
    stop = 1.0

    # Check x-crossings.
    if v[0] > 0:
      start = int(math.ceil(p[0]))
      end = int(p[0] + v[0]) + 1
      d = 1
      o = 0
    else:
      start = int(math.floor(p[0]))
      end = int(p[0] + v[0])
      d = -1
      o = -1
    for x in xrange(start, end, d):
      t = (x - p[0]) / v[0]
      y = int(p[1] + t * v[1])
      if self.CollisionMap(x + o, y):
        stop = t
        break

    # Check y-crossings.
    if v[1] > 0:
      start = int(math.ceil(p[1]))
      end = int(p[1] + v[1]) + 1
      d = 1
      o = 0
    else:
      start = int(math.floor(p[1]))
      end = int(p[1] + v[1])
      d = -1
      o = -1
    for y in xrange(start, end, d):
      t = (y - p[1]) / v[1]
      if t > stop:
        break
      x = int(p[0] + t * v[0])
      if self.CollisionMap(x, y + o):
        stop = t
        break

    p[0] += v[0] * stop
    p[1] += v[1] * stop
    p[0] /= self.collisionscale[0]
    p[1] /= self.collisionscale[1]
    return p
