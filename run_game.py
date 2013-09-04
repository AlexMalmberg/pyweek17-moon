import math
import pygame
from OpenGL import GL

import game
import mission
import renderer


def main():
  pygame.init()

  width, height = 960, 600
  flags = pygame.OPENGL | pygame.DOUBLEBUF | pygame.HWSURFACE
  if False:
    width, height = 0, 0
    flags |= pygame.FULLSCREEN

  pygame.display.set_caption('Moon')

  screen = pygame.display.set_mode((width, height), flags)

  render = renderer.Render(screen)

  m = mission.Mission('data/c0_m0.txt')
  g = game.Game(render, m)
  g.Run()


if __name__ == '__main__':
  main()
