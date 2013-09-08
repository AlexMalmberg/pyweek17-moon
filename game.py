import math
import pygame
from OpenGL import GL

import mesh
import level
import lightmap


DEBUG = True


class Player(object):
  def __init__(self, render, position):
    self.position = position
    self.light = 0
    self.frame_ids = []
    for path in ('f1', 'f2', 'f3', 'f4', 'f3', 'f2'):
      self.frame_ids.append(
        render.LoadMeshTexture('data/werewolf/%s.png' % path))

    self.move_time = 0
    self.frame_duration = 0.05

    self.Move(0, 0)

  def Move(self, dt, angle):
    self.move_time += dt
    self.move_time = math.fmod(
      self.move_time, self.frame_duration * len(self.frame_ids))
    self.current_frame = int(self.move_time / self.frame_duration)
    self.current_frame %= len(self.frame_ids)
    self.next_frame = (self.current_frame + 1) % len(self.frame_ids)
    self.blend = ((self.move_time - self.current_frame * self.frame_duration)
                  / self.frame_duration)
    self.angle = angle

  def Render(self):
    s = 18
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)

    GL.glPushMatrix()
    GL.glTranslate(self.position[0], self.position[1], 0)
    GL.glRotate(-self.angle, 0, 0, 1)

    for b, t, z in ((self.blend, self.frame_ids[self.current_frame], 0.5),
                    (1 - self.blend, self.frame_ids[self.next_frame], 0.6)):
      GL.glColor(1, 1, 1, b)
      GL.glBindTexture(GL.GL_TEXTURE_2D, t)
      GL.glBegin(GL.GL_QUADS)
      GL.glTexCoord(0, 0)
      GL.glVertex(-s, -s, z)
      GL.glTexCoord(1, 0)
      GL.glVertex( s, -s, z)
      GL.glTexCoord(1, 1)
      GL.glVertex( s,  s, z)
      GL.glTexCoord(0, 1)
      GL.glVertex(-s,  s, z)
      GL.glEnd()

    GL.glDisable(GL.GL_BLEND)
    GL.glPopMatrix()


class Moon(object):
  def __init__(self, raw_moon, level, texture_ids):
    self.angle = raw_moon['angle']
    self.angle_speed = raw_moon['angle_speed']
    self.dz = raw_moon['dz']
    self.strength = raw_moon['strength']
    self.color = map(float, raw_moon['color'])
    if 'ambient' in raw_moon:
      self.ambient = float(raw_moon['ambient'])
    else:
      self.ambient = 0

    self.update_interval = 0.25

    self.lightmaps = [lightmap.Lightmap(level, texture_ids[0]),
                      lightmap.Lightmap(level, texture_ids[1]),
                      lightmap.Lightmap(level, texture_ids[2])]

    for i in xrange(3):
      self.lightmaps[i].StartCalculation(
        *self._VectorAtTime(i * self.update_interval))
    self.lightmaps[0].FinishCalculation()
    self.lightmaps[1].FinishCalculation()

    self.blend = 0
    self.active_lightmap = 0
    self.next_lightmap = 1
    self.in_progress_lightmap = 2
    self.next_update = self.update_interval
    self.vector = self._VectorAtTime(0)

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

    self.vector = self._VectorAtTime(t)
    self.blend = ((t - self.next_update + self.update_interval)
                  / self.update_interval)
    self.lightmaps[self.in_progress_lightmap].UpdateCalculation(self.blend)

  def LightAtPosition(self, pos):
    x = int(pos[0] / 2048. * self.lightmaps[0].width)
    y = int(pos[1] / 2048. * self.lightmaps[0].height)
    if (x < 0 or y < 0 or x >= self.lightmaps[0].width
        or y >= self.lightmaps[0].height):
      return 1
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
    self.sound = 'sound' in raw_target and bool(raw_target['sound'])

  def CloseEnough(self, pos):
    dx = self.position[0] - pos[0]
    dy = self.position[1] - pos[1]
    return math.hypot(dx, dy) < self.range

  def Render(self, t):
    t = abs(math.fmod(t, 3) - 1.5) / 1.5
    GL.glEnable(GL.GL_BLEND)
    GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE)
    cx = self.position[0]
    cy = self.position[1]
    x0 = cx - self.range
    y0 = cy - self.range
    x1 = cx + self.range
    y1 = cy + self.range

    GL.glBegin(GL.GL_TRIANGLES)
    GL.glColor(t, t, 1.0, t)
    GL.glVertex(x0, y0, 1)
    GL.glVertex(x1, y0, 1)
    GL.glVertex(x1, y1, 1)

    GL.glVertex(x0, y0, 1)
    GL.glVertex(x1, y1, 1)
    GL.glVertex(x0, y1, 1)

    GL.glVertex(x0, y0, 1)
    GL.glVertex(x1, y0, 1)
    GL.glColor(t, t, 1.0, 0.0)
    GL.glVertex(cx, cy, 150)

    GL.glColor(t, t, 1.0, t)
    GL.glVertex(x0, y1, 1)
    GL.glVertex(x1, y1, 1)
    GL.glColor(t, t, 1.0, 0.0)
    GL.glVertex(cx, cy, 150)

    GL.glColor(t, t, 1.0, t)
    GL.glVertex(x0, y0, 1)
    GL.glVertex(x0, y1, 1)
    GL.glColor(t, t, 1.0, 0.0)
    GL.glVertex(cx, cy, 150)

    GL.glColor(t, t, 1.0, t)
    GL.glVertex(x1, y0, 1)
    GL.glVertex(x1, y1, 1)
    GL.glColor(t, t, 1.0, 0.0)
    GL.glVertex(cx, cy, 150)

    GL.glEnd()
    GL.glDisable(GL.GL_BLEND)


class Game(object):
  NOT_DONE = 0
  ABORTED = 1
  VICTORY = 2
  DEFEAT = 3

  def __init__(self, render, sounds, mission):
    self.render = render
    self.sounds = sounds
    self.mission = mission
    self.level = level.Level(render, mission.level_path)
    self.player = Player(render, mission.player_start)
    self.moons = []
    for m in mission.moons:
      texture_ids = render.LightmapTextureIds(len(self.moons))
      self.moons.append(Moon(m, self.level, texture_ids))

    self.ambient = mission.ambient

    self.targets = []
    for t in mission.targets:
      self.targets.append(Target(t))
    self.active_target_index = 0
    self.active_target = self.targets[0]

  def HandleInput(self, dt):
    for e in pygame.event.get():
      if (e.type == pygame.QUIT
          or (e.type == pygame.KEYDOWN
              and e.key in (pygame.K_ESCAPE, pygame.K_q))):
        self.done = self.ABORTED
        return
      if DEBUG:
        if e.type == pygame.KEYDOWN and e.key == pygame.K_SPACE:
          print 'Player at: %r' % self.player.position

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
      self.player.Move(dt, math.atan2(delta[0], delta[1]) / math.pi * 180.)

  def LightAtPosition(self, pos):
    l = 0
    for m in self.moons:
      l += m.LightAtPosition(pos)
    return l

  def DoneDefeat(self, t):
    if self.done:
      if self.done == self.DEFEAT:
        self.sounds.PlayDiscovery(t)
      return
    self.done = self.DEFEAT
    self.fade_start = t
    self.fade_end = t + 3.0
    self.fade_in = False
    self.fade_color = (0.6, 0.1, 0.1, 1)

  def DoneVictory(self, t):
    if self.done:
      return
    self.done = self.VICTORY
    self.fade_start = t
    self.fade_end = t + 3.0
    self.fade_in = False
    self.fade_color = (0, 0, 0, 1)

  def Update(self, t, dt):
    for m in self.moons:
      m.Update(t)

    if DEBUG and False:
      x, y = 438.0, 1293.0
      x = int(x / 2048. * m.lightmaps[0].width)
      y = int(y / 2048. * m.lightmaps[0].height)
      print m.lightmaps[m.active_lightmap].lightmap[y - 2:y + 2,x - 2:x + 2]

    if self.done == self.DEFEAT:
      # Hack to get the sounds to repeat even if you re-enter the shadow.
      self.DoneDefeat(t)
      return

    light = self.LightAtPosition(self.player.position)
    if light > 0:
      self.player.light += dt
      if self.player.light >= 0.1:
        self.sounds.PlayWarning(t)
      if self.player.light >= 0.8:
        self.DoneDefeat(t)
    else:
      self.player.light = 0

    if not self.done and self.active_target.CloseEnough(self.player.position):
      if self.active_target.sound:
        self.sounds.PlayTargetSound()
      self.active_target_index += 1
      if self.active_target_index == len(self.targets):
        self.DoneVictory(t)
      else:
        self.active_target = self.targets[self.active_target_index]

  def Render(self, t):
    GL.glClear(GL.GL_COLOR_BUFFER_BIT | GL.GL_DEPTH_BUFFER_BIT)

    self.render.SetupProjection(
      self.player.position[0], self.player.position[1], 700) # height

    m = self.moons[0]

    GL.glEnable(GL.GL_TEXTURE_2D)
    self.render.SetMoonlightShader(self.ambient, self.moons)
    GL.glEnable(GL.GL_DEPTH_TEST)

    self.level.Render()

    GL.glUseProgram(0)

    self.player.Render()

    GL.glDisable(GL.GL_TEXTURE_2D)

    self.active_target.Render(t)

    GL.glDisable(GL.GL_DEPTH_TEST)

    if t < self.fade_end or not self.fade_in:
      blend = (t - self.fade_start) / (self.fade_end - self.fade_start)
      blend = max(0, min(1, blend))
      if self.fade_in:
        blend = 1 - blend
      GL.glBlendFunc(GL.GL_SRC_ALPHA, GL.GL_ONE_MINUS_SRC_ALPHA)
      GL.glEnable(GL.GL_BLEND)
      GL.glColor(self.fade_color[0],
                 self.fade_color[1],
                 self.fade_color[2],
                 blend)
      self.render.FullscreenQuad()
      GL.glDisable(GL.GL_BLEND)

    pygame.display.flip()

  def Run(self):
    clock = pygame.time.Clock()
    t = 0
    self.done = self.NOT_DONE

    debug_interval = 2.0
    next_debug = 0.0

    self.level.Setup()
    self.sounds.Reset()

    self.fade_start = 0
    self.fade_end = 2.0
    self.fade_in = True
    self.fade_color = (0, 0, 0, 1)

    while True:
      if self.done == self.ABORTED:
        break
      if self.done != self.NOT_DONE and t > self.fade_end:
        break

      if DEBUG and t > next_debug:
        print clock
        next_debug += debug_interval

      dt = clock.tick() * 0.001
      if dt > 0.1:
        dt = 0.1
      t += dt

      self.HandleInput(dt)
      self.Update(t, dt)
      self.Render(t)

    self.play_time = t
    return self.done
