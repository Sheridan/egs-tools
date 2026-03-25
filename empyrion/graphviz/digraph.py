
from empyrion.graphviz.edge import CGraphEdge
from empyrion.graphviz.node import CGraphNode
from empyrion.graphviz.entity import CGraphEntity
from empyrion.options import options
from empyrion.templating import templating

class Cgraphviz(CGraphEntity):
  def __init__(self, name):
    self.name = name
    self.template_name = name
    self.nodes = []
    self.edges = []
    self.colors = {
      'background': '#1D1D1E',
      'fill'      : "#303031",
      'foregroung': "#a2a8b4",
      'font'      : '#ebf2ff'
    }
    self.fontsizes = {
      'default': 14,
      'thing_caption': 16,
      'thing_description': 12,
      'lists_caption': 10
    }
    self.iconsizes = {
      'main': 96,
      'grid': 64,
      'recipe': 48,
      'info': 24,
      'weapon': 48
    }

  def addNode(self, key, data):
    print(f"Adding node {key}")
    node = CGraphNode(key, data)
    self.nodes.append(node)

  def addEdge(self, key_from, key_to, weight):
    print(f"Adding edge {key_from} -> {key_to}")
    edge = CGraphEdge(key_from, key_to, weight)
    self.edges.append(edge)

  def prepareEntityesData(self, entityes):
    result = []
    for entity in entityes:
      result.append(entity.get())
    return result

  def render(self):
    print('Renderung .dot file')
    print(f' Nodes: {len(self.nodes)}')
    print(f' Edges: {len(self.edges)}')
    with open(f"output/graph/{self.name}.dot", 'w', encoding='utf-8') as f:
      f.write(templating.cleanString(templating.loadTemplate('graph', self.template_name).render(
                    name=self.name,
                    nodes=self.prepareEntityesData(self.nodes),
                    edges=self.prepareEntityesData(self.edges),
                    colors=self.colors,
                    fontsizes=self.fontsizes,
                    iconsizes=self.iconsizes
                  )))
