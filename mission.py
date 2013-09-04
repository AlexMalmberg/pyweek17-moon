import json

class Mission(object):
  def __init__(self, path):
    raw = json.loads(file(path).read())
    self.level_path = raw['level_path']
    self.moons = raw['moons']
    self.player_start = map(float, raw['player_start'])
