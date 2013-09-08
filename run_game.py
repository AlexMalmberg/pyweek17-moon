import math
import pygame
import sys
from OpenGL import GL

import game
import mission
import renderer


def Usage():
  print 'Usage: %s [--fullscreen] [--window widthxheight] map-name'
  sys.exit(1)


def main():
  fullscreen = False
  width, height = 960, 600
  level_path = None

  i = 1
  while i < len(sys.argv):
    if sys.argv[i] == '--fullscreen':
      fullscreen = True
    elif sys.argv[i] == '--window':
      try:
        width, height = map(int, sys.argv[i + 1].split('x'))
      except:
        Usage()
      i += 1
    elif level_path:
      Usage()
    else:
      level_path = sys.argv[i]
    i += 1

  pygame.init()

  flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
  if fullscreen:
    width, height = 0, 0
    flags |= pygame.FULLSCREEN

  pygame.display.set_caption('Moon')

  screen = pygame.display.set_mode((width, height), flags)

  render = renderer.Render(screen)

  if level_path:
    m = mission.Mission(level_path)
    g = game.Game(render, m)
    result = g.Run()
    print 'result: %i' % result
  else:
    for level_path in ('data/c0_m0.txt', 'data/c1_m0.txt', 'data/c1_m1.txt',
                       'data/c1_m2.txt'):
      m = mission.Mission(level_path)
      g = game.Game(render, m)
      result = g.Run()
      if result != game.Game.VICTORY:
        break


if __name__ == '__main__':
  main()
