
from empyrion.graphviz.entity import CGraphEntity

class CGraphEdge(CGraphEntity):
  def __init__(self, key_from, key_to, weight):
    self.key_from = key_from
    self.key_to = key_to
    self.weight = weight

  def get(self):
    return { 'key_from' : self.key_from,
             'key_to'   : self.key_to,
             'weight'   : self.weight
           }
