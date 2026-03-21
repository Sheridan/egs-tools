import csv

class CCsv:
  def __init__(self, filename, src_language_column, dst_language_column):
    self.filename = filename
    self.src_language_column = src_language_column
    self.dst_language_column = dst_language_column
    self.headers = None
    self.data = {}
    self.changed = False
    self._load()

  def _load(self):
    with open(self.filename, 'r', encoding='utf-8') as f:
      reader = csv.reader(f)
      self.headers = next(reader, None)
      # print(self.headers)

      if not self.headers:
        raise ValueError(f"Пустой файл {self.filename}")

      for row in reader:
        self.data[row[0]] = row[1:]

  def save(self):
    self.saveAs(self.filename)

  def saveAs(self, filename):
    with open(filename, 'w', newline='') as f:
      writer = csv.writer(f)
      writer.writerow(self.headers)
      # print(self.data)
      for key in self.data.keys():
        writer.writerow([key] + list(self.data[key]))

  def __del__(self):
    if self.changed:
      self.save()

  def keys(self):
    return list(self.data.keys())

  def get(self, key, column):
    return self.data[key][column]

  def get_src_language(self, key):
    return self.get(key, self.src_language_column)

  def get_dst_language(self, key):
    return self.get(key, self.dst_language_column)

  def set(self, key, column, value):
    self.data[key][column] = value
    self.changed = True

  def set_dst_language(self, key, value):
    self.set(key, self.dst_language_column, value)
