
from empyrion.graphviz.edge import CGraphEdge
from empyrion.graphviz.node import CGraphNode

class Cgraphviz:
  def __init__(self, name):
    self.name = name
    self.nodes = []
    self.edges = []

  def addNode(self, name, template_name):
    node = CGraphNode(name, template_name)
    self.nodes.append(node)

  def addEdge(self, name_from, name_to, template_name):
    edge = CGraphEdge(name_from, name_to, template_name)
    self.edges.append(edge)

  def render(self):
    with open(f"output/{self.name}.dot", 'w', encoding='utf-8') as f:
      f.write("digraph g{\n")
      f.write("graph [\n")
      f.write("overlap=false;\n")
      # f.write("splines=true;\n")
      f.write("ranksep=0.3;\n")
      f.write("nodesep=0.1;\n")
      f.write("];\n")
      for node in self.nodes:
        f.write(f"{node.render()}\n")
      for edge in self.edges:
        f.write(f"{edge.render()}\n")
      f.write("}\n")
