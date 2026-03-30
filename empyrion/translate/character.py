
class CCharacter:
  def __init__(self):
    self._data = {}
    self._load()

  def _load(self):
    with open("characters/Russian.json", 'r', encoding='utf-8') as f:
      self._data = f.read().strip()
