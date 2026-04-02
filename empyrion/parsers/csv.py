import csv
import re
from rich import print as rprint
import empyrion.helpers.color as clr

class CCsv:
  def __init__(self, filename, src_language, dst_language):
    self._filename = filename
    self._headers = None
    self._data = {}
    self._changed = False
    self._load()
    self._src_language_column = self.head_title_index(src_language) - 1
    self._dst_language_column = self.head_title_index(dst_language) - 1
    # self._set_queries = 0

  def _load(self):
    rprint(clr.loadf(self._filename))
    with open(self._filename, 'r', encoding='utf-8') as f:
      reader = csv.reader(f)
      self._headers = next(reader, None)
      # print(self._headers)

      if not self._headers:
        raise ValueError(f"Пустой файл {self._filename}")

      for row in reader:
        for i in range(len(row), len(self._headers)):
          row.append('')
        self._data[row[0]] = row[1:]

  def save(self):
    self.saveAs(self._filename)

  def saveAs(self, filename):
    with open(filename, 'w', newline='') as f:
      rprint(clr.savef(self._filename))
      writer = csv.writer(f)
      writer.writerow(self._headers)
      # print(self._data)
      for key in self._data:
        writer.writerow([key] + list(self._data[key]))
    self._changed = False

  #def __del__(self):
  #  if self._changed:
  #    self.save()

  def keys(self):
    return self._data.keys()

  def get(self, key, column):
    return self._data[key][column]

  def exists(self, key):
    return key in self._data

  def count(self):
    return len(self._data)

  def get_src_language(self, key):
    return self.get(key, self._src_language_column)

  def get_dst_language(self, key):
    return self.get(key, self._dst_language_column)

  def set(self, key, column, value):
    self._data[key][column] = value
    self._changed = True
    # self._set_queries += 1
    # if self._set_queries >= options.get("translation.save_every_nth_query", 10):
    #   self.save()
    #   self._set_queries = 0

  def set_dst_language(self, key, value):
    self.set(key, self._dst_language_column, value)

  def head_title_index(self, name):
    i = 0
    for item in self._headers:
      if item == name:
        return i
      i += 1
