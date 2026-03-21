from string import Template

class CGraphEntity:
  def cleanLabel(self, label):
    # return re.sub(r"[\.x]")
    return label.replace('.', '_')

  def loadTemplate(self, type, name):
    with open(f"templates/graph/{type}/{name}.tpl", 'r', encoding='utf-8') as f:
      return Template(f.read().strip())
