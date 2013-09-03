import math
import pygame
from OpenGL import GL

import level
import lightmap
import game


def main():
  pygame.init()

  width, height = 960, 600
  flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
  if False:
    width, height = 0, 0
    flags |= pygame.FULLSCREEN

  pygame.display.set_caption('Moon')

  screen = pygame.display.set_mode((width, height), flags)
  width = screen.get_width()
  height = screen.get_height()
  GL.glViewport(0, 0, width, height)
  GL.glClear(GL.GL_COLOR_BUFFER_BIT)
  pygame.display.flip()

  lvl = level.Level('data/test_map')
  g = game.Game(lvl)
  light = lightmap.Lightmap(lvl, 1)
  print 'a'
  for i in xrange(36):
    a = 2 / 36. * 2 * math.pi
    light.StartCalculation(math.cos(a), math.sin(a), 1.0)
    light.FinishCalculation()
    #f = file('%i.data' % i, 'w')
    #f.write(light.lightmap.tostring())
    #f.close()
  #print light.lightmap
  print 'c'
  while True:
    x = 1


if __name__ == '__main__':
  main()
