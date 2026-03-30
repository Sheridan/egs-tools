import statistics

class CHistory:
  def __init__(self):
    self._data = []

  def append(self, measurments):
    self._data += measurments

  def count(self):
    return len(self._data)

  def mean(self):
    return statistics.mean(self._data)

  def median(self):
    return statistics.median(self._data)

  def sum(self):
    return sum(self._data)

  def max(self):
    return max(self._data)

  def min(self):
    return min(self._data)
