
import re
import pprint

from empyrion.graphviz.digraph import Cgraphviz
from empyrion.definition import definition
from empyrion.translation import translation

class CGraph:
  def __init__(self):
    self.graphviz = Cgraphviz("main")

  def translatedKey(self, key):
    if translation.localization.keyExists(key):
      text = translation.localization.get_src_language(key)
      return re.sub(r'\[.*?\]', '', text).replace('\\n', ' ')
    return key

  def translatedItem(self, key):
    caption = self.translatedKey(key)
    description = self.translatedKey(f"{key}info")
    return (caption, description)

  def itemCanBeGraphed(self, item):
    if "Target" not in item: return False
    # if item['Target'] == '' or item['Target'] == '""': return False
    return True

  def construct(self):
    for key in definition.templates.names():
      item = definition.templates.get(key)
      if self.itemCanBeGraphed(item):
        captdesc = self.translatedItem(key)
        print(f"{key}: {captdesc[0]} ({captdesc[1]})")
        # pprint.pprint(item)
        self.graphviz.addNode(key, "item")
      if 'Child' in item and 'Inputs' in item['Child']:
        for input in item['Child']['Inputs'][0].keys():
          count = int(item['Child']['Inputs'][0][input])
          if count > 0:
            self.graphviz.addEdge(key, input, 'item')
      self.graphviz.render()
