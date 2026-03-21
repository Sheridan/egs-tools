from empyrion.graphviz.entity import CGraphEntity

class CGraphNode(CGraphEntity):
  def __init__(self, name, template_name):
    self.name = name
    self.template_name = template_name

  def render(self):
    return self.loadTemplate('node', self.template_name).safe_substitute(
                    name=self.cleanLabel(self.name)
                  )
    # return f"node_{} [shape=box];"
