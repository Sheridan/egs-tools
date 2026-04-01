from empyrion.graphviz.entity import CGraphEntity

class CGraphNode(CGraphEntity):
  def __init__(self, key, data):
    self._key = key
    self._data = data

  def get(self):
    return {  "key":  self._key,
              "data": self._data  }
