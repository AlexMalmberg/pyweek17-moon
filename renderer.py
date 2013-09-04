import pygame
from OpenGL.GL import *

class Render(object):
  def __init__(self, screen):
    width = screen.get_width()
    height = screen.get_height()
    glViewport(0, 0, width, height)
    glClear(GL_COLOR_BUFFER_BIT)
    pygame.display.flip()
    self.aspect_ratio = width / float(height)

    # We hand out all texture ids here by 'user' and never delete any
    # of them toavoid problems with trying to make sure we don't leak
    # them as objects get created and destroyed.
    self.lightmap_ids = {}

  def SetupProjection(self, x, y, height):
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    glFrustum(-self.aspect_ratio, self.aspect_ratio,
               -1, 1,
               1, height + 4)
    glTranslate(-x, -y, -height)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

  def LoadTexture(self, path):
    s = pygame.image.load(path)
    id = glGenTextures(1)
    raw = pygame.image.tostring(s, 'RGBA', 1)
    w, h = s.get_width(), s.get_height()
    glBindTexture(GL_TEXTURE_2D, id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER,
                    GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER,
                    GL_LINEAR_MIPMAP_LINEAR)
    glTexParameter(GL_TEXTURE_2D, GL_GENERATE_MIPMAP, GL_TRUE)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP)
    glTexParameter(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, w, h, 0, GL_RGBA,
                 GL_UNSIGNED_BYTE, raw)
    return id


  def LightmapTextureIds(self, index):
    if index not in self.lightmap_ids:
      self.lightmap_ids[index] = glGenTextures(3)
    return self.lightmap_ids[index]
