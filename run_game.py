import math
import pygame
import sys
from OpenGL import GL

import game
import mission
import renderer
import sounds


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
  snds = sounds.Sounds()

  if level_path:
    print 'Debugging map %s.' % level_path
    m = mission.Mission(level_path)
    g = game.Game(render, snds, m)
    result = g.Run()
    print 'Result: %i, took %0.1f seconds' % (result, g.play_time)
  else:
    levels =  ('data/c0_m0.txt', 'data/c1_m0.txt', 'data/c1_m1.txt',
               'data/c1_m2.txt')
    par_times = (72.5, 29.2, 89.6, 88.4)
    play_times = [None] * len(levels)
    i = 0
    while i < len(levels):
      level_path = levels[i]
      m = mission.Mission(level_path)
      g = game.Game(render, snds, m)
      result = g.Run()
      if result == game.Game.ABORTED:
        break
      if result == game.Game.VICTORY:
        play_times[i] = g.play_time
        i += 1

    if i > 0:
      print 'Your times:'
      for i, (play_time, par_time) in enumerate(zip(play_times, par_times)):
        if play_time is None:
          continue
        print ('Mission %i: %5.1fs    Par time: %5.1fs'
               % (i + 1, play_time, par_time))


if __name__ == '__main__':
  main()
