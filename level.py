import json
import math
import numpy
import pygame
from OpenGL import GL

import mesh


class LevelMesh(object):
  def __init__(self, render, raw_mesh):
    self.mesh = mesh.Mesh(raw_mesh['obj_path'])
    if 'texture_path' in raw_mesh:
      self.texture = render.LoadMeshTexture(raw_mesh['texture_path'])
    else:
      self.texture = render.white_texture
    self.center = tuple(map(float, raw_mesh['center']))
    if 'scale' in raw_mesh:
      self.scale = tuple(map(float, raw_mesh['scale']))
    else:
      self.scale = (1, 1, 1)
    if 'angle' in raw_mesh:
      self.angle = float(raw_mesh['angle'])
    else:
      self.angle = 0

  def Render(self):
    GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
    self.mesh.Render(self.center, self.scale, self.angle)


class Level(object):
  def __init__(self, render, path, load_maps=True):
    self.render = render
    self.raw = json.loads(file(path + '/level.txt').read())

    if load_maps:
      surface = pygame.image.load(path + '/height.png')
      raw_heightmap = pygame.image.tostring(surface, 'P', 1)
      self.heightmap = numpy.fromstring(raw_heightmap, dtype=numpy.uint8)
      self.heightmap.shape = (surface.get_height(), surface.get_width())

      # TODO(alex): just build a coarse bsp tree of the geometry?
      surface = pygame.image.load(path + '/collision.png')
      raw_collisionmap = pygame.image.tostring(surface, 'P', 1)
      self.collisionmap = numpy.fromstring(raw_collisionmap, dtype=numpy.uint8)
      w, h = surface.get_width(), surface.get_height()
      self.collisionmap.shape = (h, w)
      self.collisionscale = [w / 2048., h / 2048.]

    self.texture_path = path + '/texture.png'

  def Setup(self):
    self.texture = self.render.LoadGroundTexture(self.texture_path)
    self.meshes = []
    for raw_mesh in self.raw['meshes']:
      self.meshes.append(LevelMesh(self.render, raw_mesh))

  def Render(self):
    GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
    GL.glBegin(GL.GL_QUADS)
    GL.glNormal(0, 0, 1)
    GL.glTexCoord(0, 0)
    GL.glVertex(0, 0)
    GL.glTexCoord(1, 0)
    GL.glVertex(2048, 0)
    GL.glTexCoord(1, 1)
    GL.glVertex(2048, 2048)
    GL.glTexCoord(0, 1)
    GL.glVertex(0, 2048)
    GL.glEnd()

    for m in self.meshes:
      m.Render()

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
