import pygame
import random


class Sounds(object):
  def __init__(self):
    self.warnings = []
    for i in xrange(1, 9):
      self.warnings.append(pygame.mixer.Sound(
          'data/voices/warnings/s%i.ogg' % i))

    self.disc = []
    for i in xrange(1, 4):
      self.disc.append(pygame.mixer.Sound(
          'data/voices/discovered/s%i.ogg' % i))

    self.crunchy = pygame.mixer.Sound('data/voices/crunchy.ogg')

    self.Reset()

  def Reset(self):
    self.next_warning = 0.0
    self.next_discovery = 0.0
    pygame.mixer.fadeout(250)

  def PlayTargetSound(self):
    pygame.mixer.Channel(4).play(self.crunchy)

  def PlayWarning(self, t):
    if t < self.next_warning:
      return
    snd = random.choice(self.warnings)
    pygame.mixer.Channel(0).play(snd)
    self.next_warning = t + snd.get_length() + 0.5

  def PlayDiscovery(self, t):
    if t < self.next_discovery:
      return
    d = random.randint(0, len(self.disc) - 1)
    snd = self.disc[d]
    ch = pygame.mixer.Channel(d + 1)
    if not ch.get_busy():
      pygame.mixer.Channel(d + 1).play(snd)
    self.next_discovery = t + 0.05
    self.next_warning = t + snd.get_length() + 5.0
