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

    for xadj in (0, -0.1, 0.1):
      for yadj in (0, -0.1, 0.1):
        x = int(p[0] + xadj)
        y = int(p[1] + yadj)
        if not self.CollisionMap(x, y):
          break
      else:
        continue
      break

    dst_x = int(p[0] + v[0])
    dst_y = int(p[1] + v[1])
    #print ('p=%0.2f, %0.2f, xy = %i, %i, dst=%0.2f, %0.2f, dst_xy=%i, %i'
    #       % (p[0], p[1], x, y, p[0] + v[0], p[1] + v[1], dst_x, dst_y))

    # TODO(alex): this is seriously ugly. if there's time, switch to
    # geometry based approach
    if x < dst_x:
      while x < dst_x:
        if self.CollisionMap(x + 1, y):
          break
        x += 1
      cx = x
      if x == dst_x:
        x = p[0] + v[0]
      else:
        x = x + 1
    elif x > dst_x:
      while x > dst_x:
        if self.CollisionMap(x - 1, y):
          break
        x -= 1
      cx = x
      if x == dst_x:
        x = p[0] + v[0]
    else:
      cx = x
      x = p[0] + v[0]

    if y < dst_y:
      while y < dst_y:
        if self.CollisionMap(cx, y + 1):
          break
        y += 1
      if y == dst_y:
        y = p[1] + v[1]
      else:
        y = y + 1
    elif y > dst_y:
      while y > dst_y:
        if self.CollisionMap(cx, y - 1):
          break
        y -= 1
      if y == dst_y:
        y = p[1] + v[1]
    else:
      y = p[1] + v[1]

    p[0] = x / self.collisionscale[0]
    p[1] = y / self.collisionscale[1]
    return p
