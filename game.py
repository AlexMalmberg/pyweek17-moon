import math
import pygame
from OpenGL import GL

import level
import lightmap


class Player(object):
  def __init__(self, position):
    self.position = position
    self.light = 0

  def Render(self):
    GL.glColor(self.light, 1, 0.0)
    GL.glBegin(GL.GL_QUADS)
    GL.glVertex(self.position[0] - 8, self.position[1] - 8)
    GL.glVertex(self.position[0] + 8, self.position[1] - 8)
    GL.glVertex(self.position[0] + 8, self.position[1] + 8)
    GL.glVertex(self.position[0] - 8, self.position[1] + 8)
    GL.glEnd()


class Cube(object):
  def __init__(self, x0, y0, x1, y1, h):
    self.x0 = x0
    self.y0 = 2048 - y0
    self.x1 = x1
    self.y1 = 2048 - y1
    self.h = h

  def Render(self):
    GL.glEnable(GL.GL_DEPTH_TEST)
    GL.glBegin(GL.GL_QUADS)

    GL.glColor(0.2, 0.2, 0.8)
    GL.glVertex(self.x0, self.y0, 0)
    GL.glVertex(self.x1, self.y0, 0)
    GL.glVertex(self.x1, self.y0, self.h)
    GL.glVertex(self.x0, self.y0, self.h)

    GL.glColor(0.2, 0.2, 0.7)
    GL.glVertex(self.x1, self.y0, 0)
    GL.glVertex(self.x1, self.y1, 0)
    GL.glVertex(self.x1, self.y1, self.h)
    GL.glVertex(self.x1, self.y0, self.h)

    GL.glColor(0.2, 0.2, 0.6)
    GL.glVertex(self.x1, self.y1, 0)
    GL.glVertex(self.x0, self.y1, 0)
    GL.glVertex(self.x0, self.y1, self.h)
    GL.glVertex(self.x1, self.y1, self.h)

    GL.glColor(0.2, 0.2, 0.5)
    GL.glVertex(self.x0, self.y1, 0)
    GL.glVertex(self.x0, self.y0, 0)
    GL.glVertex(self.x0, self.y0, self.h)
    GL.glVertex(self.x0, self.y1, self.h)

    GL.glColor(0.3, 0.3, 1.0)
    GL.glVertex(self.x0, self.y0, self.h)
    GL.glVertex(self.x1, self.y0, self.h)
    GL.glVertex(self.x1, self.y1, self.h)
    GL.glVertex(self.x0, self.y1, self.h)

    GL.glEnd()
    GL.glDisable(GL.GL_DEPTH_TEST)


class Moon(object):
  def __init__(self, raw_moon, level, texture_ids):
    print 'Moon.__init__'
    self.angle = raw_moon['angle']
    self.angle_speed = raw_moon['angle_speed']
    self.dz = raw_moon['dz']
    self.strength = raw_moon['strength']
    self.color = map(float, raw_moon['color'])

    self.update_interval = 0.25

    self.lightmaps = [lightmap.Lightmap(level, texture_ids[0]),
                      lightmap.Lightmap(level, texture_ids[1]),
                      lightmap.Lightmap(level, texture_ids[2])]

    print 'Moon.__init__ create lightmaps'
    for i in xrange(3):
      self.lightmaps[i].StartCalculation(
        *self._VectorAtTime(i * self.update_interval))
    print 'Moon.__init__ finish map 0, 1 calculations'
    self.lightmaps[0].FinishCalculation()
    self.lightmaps[1].FinishCalculation()
    print 'Moon.__init__ done'

    self.blend = 0
    self.active_lightmap = 0
    self.next_lightmap = 1
    self.in_progress_lightmap = 2
    self.next_update = self.update_interval

  def _VectorAtTime(self, t):
    a = self.angle + self.angle_speed * t
    return math.cos(a), math.sin(a), self.dz

  def Update(self, t):
    if t > self.next_update:
      # TODO(alex): properly skip time forward if we miss an
      # update. lopri since dt is capped
      while t > self.next_update:
        self.next_update += self.update_interval
      self.lightmaps[self.in_progress_lightmap].FinishCalculation()
      self.active_lightmap = (self.active_lightmap + 1) % 3
      self.next_lightmap = (self.next_lightmap + 1) % 3
      self.in_progress_lightmap = (self.in_progress_lightmap + 1) % 3
      self.lightmaps[self.in_progress_lightmap].StartCalculation(
        *self._VectorAtTime(self.next_update + self.update_interval))

    self.blend = ((t - self.next_update + self.update_interval)
                  / self.update_interval)
    self.lightmaps[self.in_progress_lightmap].UpdateCalculation(self.blend)

  def LightAtPosition(self, pos):
    x = int(pos[0] / 2048. * self.lightmaps[0].width)
    y = int(pos[1] / 2048. * self.lightmaps[1].width)
    if self.lightmaps[self.active_lightmap].lightmap[y][x] > 0:
      l0 = 0
    else:
      l0 = 1
    if self.lightmaps[self.next_lightmap].lightmap[y][x] > 0:
      l1 = 0
    else:
      l1 = 1
    l = l0 * (1 - self.blend) + l1 * self.blend
    return l * self.strength


class Target(object):
  def __init__(self, raw_target):
    self.position = map(float, raw_target['position'])
    self.range = float(raw_target['range'])

  def CloseEnough(self, pos):
    dx = self.position[0] - pos[0]
    dy = self.position[1] - pos[1]
    return math.hypot(dx, dy) < self.range

  def Render(self, t):
    t = abs(math.fmod(t, 3) - 1.5) / 1.5
    GL.glColor(t, t, 1.0)
    GL.glBegin(GL.GL_QUADS)
    GL.glVertex(self.position[0] - self.range, self.position[1] - self.range)
    GL.glVertex(self.position[0] + self.range, self.position[1] - self.range)
    GL.glVertex(self.position[0] + self.range, self.position[1] + self.range)
    GL.glVertex(self.position[0] - self.range, self.position[1] + self.range)
    GL.glEnd()


class Game(object):
  NOT_DONE = 0
  ABORTED = 1
  VICTORY = 2
  DEFEAT = 3

  def __init__(self, render, mission):
    print 'Game.__init__'
    self.render = render
    self.mission = mission
    self.level = level.Level(mission.level_path)
    self.player = Player(mission.player_start)
    self.moons = []
    for m in mission.moons:
      texture_ids = render.LightmapTextureIds(len(self.moons))
      self.moons.append(Moon(m, self.level, texture_ids))

    self.targets = []
    for t in mission.targets:
      self.targets.append(Target(t))
    self.active_target_index = 0
    self.active_target = self.targets[0]

    self.texture = render.LoadTexture('data/test_map/texture1.png')

    self.hack_meshes = []
    self.hack_meshes.append(Cube(290, 644, 587, 867, 102))
    self.hack_meshes.append(Cube(887, 745, 1334, 1027, 102))
    self.hack_meshes.append(Cube(827, 291, 1400, 622, 108))

  def HandleInput(self, dt):
    for e in pygame.event.get():
      if (e.type == pygame.QUIT
          or (e.type == pygame.KEYDOWN
              and e.key in (pygame.K_ESCAPE, pygame.K_q))):
        self.done = self.ABORTED
        return

    pressed = pygame.key.get_pressed()
    delta = [0, 0]
    if pressed[pygame.K_UP]:
      delta[1] = 1
    if pressed[pygame.K_DOWN]:
      delta[1] = -1
    if pressed[pygame.K_LEFT]:
      delta[0] = -1
    if pressed[pygame.K_RIGHT]:
      delta[0] = 1

    if delta[0] or delta[1]:
      speed = 120.
      delta[0] *= dt * speed
      delta[1] *= dt * speed
      self.player.position = self.level.Move(self.player.position, delta)

  def LightAtPosition(self, pos):
    l = 0
    for m in self.moons:
      l += m.LightAtPosition(pos)
    return l

  def Update(self, t, dt):
    for m in self.moons:
      m.Update(t)

    light = self.LightAtPosition(self.player.position)
    if light > 0:
      self.player.light += dt * light / 1.0
      if self.player.light >= 1:
        self.done = self.DEFEAT
    else:
      self.player.light = 0

    if not self.done and self.active_target.CloseEnough(self.player.position):
      print 'trigger %i' % self.active_target_index
      self.active_target_index += 1
      if self.active_target_index == len(self.targets):
        self.done = self.VICTORY
      else:
        self.active_target = self.targets[self.active_target_index]

  def Render(self, t):
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    self.render.SetupProjection(
      self.player.position[0], self.player.position[1], 700)

    m = self.moons[0]

    GL.glEnable(GL.GL_TEXTURE_2D)
    GL.glBindTexture(GL.GL_TEXTURE_2D, self.texture)
    GL.glColor(0.7, 0.7, 0.7)
    GL.glBegin(GL.GL_QUADS)
    GL.glTexCoord(0, 0)
    GL.glVertex(0, 0)
    GL.glTexCoord(1, 0)
    GL.glVertex(2048, 0)
    GL.glTexCoord(1, 1)
    GL.glVertex(2048, 2048)
    GL.glTexCoord(0, 1)
    GL.glVertex(0, 2048)
    GL.glEnd()

    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_ZERO, GL.GL_ONE_MINUS_SRC_ALPHA)

    GL.glBindTexture(GL.GL_TEXTURE_2D, m.lightmaps[m.active_lightmap].id)
    if True:
      GL.glColor(0, 0, 0, 1 - m.blend)
    else:
      GL.glColor(0, 0, 0, 1)
    GL.glBegin(GL.GL_QUADS)
    GL.glTexCoord(0, 0)
    GL.glVertex(0, 0)
    GL.glTexCoord(1, 0)
    GL.glVertex(2048, 0)
    GL.glTexCoord(1, 1)
    GL.glVertex(2048, 2048)
    GL.glTexCoord(0, 1)
    GL.glVertex(0, 2048)
    GL.glEnd()

    if True:
      GL.glBindTexture(GL.GL_TEXTURE_2D, m.lightmaps[m.next_lightmap].id)
      GL.glColor(0, 0, 0, m.blend)
      GL.glBegin(GL.GL_QUADS)
      GL.glTexCoord(0, 0)
      GL.glVertex(0, 0)
      GL.glTexCoord(1, 0)
      GL.glVertex(2048, 0)
      GL.glTexCoord(1, 1)
      GL.glVertex(2048, 2048)
      GL.glTexCoord(0, 1)
      GL.glVertex(0, 2048)
      GL.glEnd()

    GL.glDisable(GL.GL_BLEND)
    GL.glDisable(GL.GL_TEXTURE_2D)

    for hm in self.hack_meshes:
      hm.Render()

    self.player.Render()
    self.active_target.Render(t)

    pygame.display.flip()

  def Run(self):
    clock = pygame.time.Clock()
    t = 0
    self.done = self.NOT_DONE

    debug_interval = 2.0
    next_debug = 0.0

    while self.done == self.NOT_DONE:
      if t > next_debug:
        print clock
        next_debug += debug_interval

      dt = clock.tick() * 0.001
      if dt > 0.1:
        dt = 0.1
      t += dt

      self.HandleInput(dt)
      self.Update(t, dt)
      self.Render(t)

    return self.done
