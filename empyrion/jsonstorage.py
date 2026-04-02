import json
import os

from rich import print as rprint

import empyrion.helpers.color as clr

class CJsonStorage:
  def __init__(self, filename):
    self._filename = filename
    self._data = {}
    self._load()

  def _load(self):
    if not os.path.exists(self._filename):
      return
    try:
      rprint(clr.loadf(self._filename))
      with open(self._filename, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if not content:
          return
        self._data = json.loads(content)
    except (json.JSONDecodeError, IOError):
      self._data = {}

  def save(self):
    rprint(clr.savef(self._filename))
    dir_name = os.path.dirname(self._filename)
    if dir_name:
      os.makedirs(dir_name, exist_ok=True)

    with open(self._filename, 'w', encoding='utf-8') as f:
      json.dump(self._data, f, ensure_ascii=False, indent=2)

  def _ensureSectionExists(self, tool, section):
    if tool not in self._data:
      self._data[tool] = {}
    if section not in self._data[tool]:
      self._data[tool][section] = {}

  def _toolExists(self, tool):
    return tool in self._data

  def _sectionExists(self, tool, section):
    if not self._toolExists(tool):
      return False
    return section in self._data[tool]

  # list
  def _add(self, tool, section, name, value):
    self._ensureSectionExists(tool, section)
    if name not in self._data[tool][section]:
      self._data[tool][section][name] = list()
    if value not in self._data[tool][section][name]:
      self._data[tool][section][name].append(value)

  # dict
  def _set(self, tool, section, name, value):
    self._ensureSectionExists(tool, section)
    # if name not in self._data[tool][section]:
    #   self._data[tool][section][name] = dict()
    self._data[tool][section][name] = value

  def _last(self, tool, section, name, default):
    section = self._section(tool, section)
    if section is not None and name in section:
      if isinstance(section[name], list):
        return section[name][-1]
      return section[name]
    return default

  def _tool(self, tool):
    if self._toolExists(tool):
      return self._data[tool]
    return None

  def _section(self, tool, section):
    if self._sectionExists(tool, section):
      return self._data[tool][section]
    return None
