
from empyrion.graphviz.entity import CGraphEntity

class CGraphEdge(CGraphEntity):
  def __init__(self, name_from, name_to, template_name):
    self.name_from = name_from
    self.name_to = name_to
    self.template_name = template_name

  def render(self):
    return self.loadTemplate('edge', self.template_name).safe_substitute(
                    name_from=self.cleanLabel(self.name_from),
                    name_to=self.cleanLabel(self.name_to)
                  )
    # return f"node_{self.cleanLabel(self.name_from)} -> node_{self.cleanLabel(self.name_to)};"
