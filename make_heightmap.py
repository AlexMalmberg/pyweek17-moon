import ctypes
import pygame
import sys
from OpenGL.GL import *

import level
import renderer


depth_vshader = """
#version 110

varying vec4 position;

void main() {
  gl_Position = gl_ModelViewProjectionMatrix * gl_Vertex;
  position = gl_ModelViewMatrix * gl_Vertex;
}
"""

depth_fshader = """
#version 110

varying vec4 position;

void main() {
  gl_FragColor = vec4(
    position.z / 255.,
    0, //position.x / 2048.,
    0, //position.y / 2048.,
    0);
}
"""


def main():
  pygame.init()
  lsize = (2048, 2048)
  size = (1024, 1024)
  chunk = (1024, 512)
  s = pygame.display.set_mode(chunk, pygame.OPENGL | pygame.HWSURFACE)
  r = renderer.Render(s)

  path = sys.argv[1]
  lvl = level.Level(r, path)
  glUseProgram(renderer.CompileProgram(depth_vshader, depth_fshader))
  lvl.Setup()

  chunks = (size[0] / chunk[0], size[1] / chunk[1])

  glEnable(GL_DEPTH_TEST)

  o = file(path + '/height.pnm', 'wb')
  o.write('P5 %i %i 255\n' % size)

  for cy in xrange(chunks[1]):
    for cx in xrange(chunks[0]):
      glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
      glMatrixMode(GL_PROJECTION)
      glLoadIdentity()

      x0 = cx * chunk[0] * lsize[0] / size[0]
      x1 = (cx + 1) * chunk[0] * lsize[0] / size[0]
      y0 = cy * chunk[01] * lsize[1] / size[1]
      y1 = (cy + 1) * chunk[1] * lsize[1] / size[1]
      print x0, y0, x1, y1
      glOrtho(x0, x1, y0, y1, -1, 257)

      glTranslate(0, 0, -256)
      glMatrixMode(GL_MODELVIEW)

      lvl.Render()
      pygame.display.flip()

      buf = ctypes.create_string_buffer(chunk[0] * chunk[1])
      glReadPixels(0, 0, chunk[0], chunk[1], GL_RED, GL_UNSIGNED_BYTE, buf)
      o.write(buf)

  o.close()


if __name__ == '__main__':
  main()
