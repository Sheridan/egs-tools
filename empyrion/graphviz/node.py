from empyrion.graphviz.entity import CGraphEntity

class CGraphNode(CGraphEntity):
  def __init__(self, key, data):
    self.key = key
    self.data = data

  def get(self):
    return {  "key":  self.key,
              "data": self.data  }
