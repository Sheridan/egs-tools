import json
import os
from typing import List

class StateStorage:
  def __init__(self, filename, save_step = 1):
    self.filename = filename
    self.save_step = save_step
    self.set_count = 0
    self._cache = set()
    self._load()

  def _load(self):
    if not os.path.exists(self.filename):
      return

    try:
      with open(self.filename, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if not content:
          return
        data = json.loads(content)
        if isinstance(data, list):
          self._cache = set(data)
    except (json.JSONDecodeError, IOError):
      self._cache = set()

  def _save(self):
    dir_name = os.path.dirname(self.filename)
    if dir_name:
      os.makedirs(dir_name, exist_ok=True)

    with open(self.filename, 'w', encoding='utf-8') as f:
      json.dump(list(self._cache), f, ensure_ascii=False)

  def set(self, state_string: str):
    self._cache.add(state_string)
    self.set_count += 1
    if self.set_count >= self.save_step:
      self._save()
      self.set_count = 0

  def exists(self, state_string: str) -> bool:
    return state_string in self._cache

  def get_all(self) -> List[str]:
    return list(self._cache)
