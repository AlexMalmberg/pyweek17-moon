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

    # texture(s)

  def Render(self):
    pass

  def Move(self, p, v):
    pass
