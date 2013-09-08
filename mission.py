import json

class Mission(object):
  def __init__(self, path):
    raw = json.loads(file(path).read())
    self.level_path = raw['level_path']
    self.moons = raw['moons']
    self.targets = raw['targets']
    self.player_start = map(float, raw['player_start'])
    if 'ambient' in raw:
      self.ambient = map(float, raw['ambient'])
    else:
      self.ambient = (0.4, 0.4, 0.4, 1.0)

