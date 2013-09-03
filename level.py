import pygame


class Level(object):
  def __init__(self, path):
    surface = pygame.image.load(path + '/height.png')
    self.heightmap = pygame.image.tostring(surface, 'P', 1)
    self.heightdim = (surface.get_width(), surface.get_height())

    # texture(s)
    # heightmap

    # collisionmap
    # pathfindingmap?
    # TODO(alex): or just build a coarse bsp tree of the geometry?

  def Render(self):
    pass
