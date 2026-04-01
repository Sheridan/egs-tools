import json

class COptions:
  def __init__(self, filename):
    self._filename = filename
    self._data = {}
    self._load()

  def _load(self):
    try:
      with open(self._filename, 'r', encoding='utf-8') as f:
        self._data = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
      self._data = {}

  def get(self, path, default=None):
    keys = path.split('.')
    value = self._data

    for key in keys:
      if isinstance(value, dict) and key in value:
        value = value[key]
      else:
        return default

    return value

options = COptions("options.json")
