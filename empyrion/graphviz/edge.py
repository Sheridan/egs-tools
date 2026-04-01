
from empyrion.graphviz.entity import CGraphEntity

class CGraphEdge(CGraphEntity):
  def __init__(self, key_from, key_to, weight):
    self._key_from = key_from
    self._key_to = key_to
    self._weight = weight

  def get(self):
    return { 'key_from' : self._key_from,
             'key_to'   : self._key_to,
             'weight'   : self._weight
           }
