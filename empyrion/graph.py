import re
import pprint

from empyrion.graphviz.digraph import Cgraphviz
from empyrion.model.things import things
from empyrion.options import options

class CGraph:
  def __init__(self):
    self._graphviz = Cgraphviz("main")

  def _thingLog(self, thing):
    print("------------------------------------------------------------------")
    print(f"{thing['things_keys']['thing']}")
    pprint.pprint(thing)
    print("------------------------------------------------------------------")

  def construct(self):
    for thing in things.things():
      if options.get("debug", False):
        self._thingLog(thing)
      self._graphviz.addNode(thing['things_keys']['thing'], thing)
      if thing['hasCrafting']:
        for ingridient_key in thing['recipe']['Child']['Inputs'].keys():
          count = int(thing['recipe']['Child']['Inputs'][ingridient_key])
          if count > 0:
#            self.copy_icon(src_icon_name, thing['things_keys']['thing'])
            self._graphviz.addEdge(thing['things_keys']['thing'], ingridient_key, 1)
      if 'weapon' in thing:
        if thing['weapon']['weapon_or_ammo'] == 'weapon' and 'ammo' in thing['weapon'] and thing['weapon']['ammo']:
          self._graphviz.addEdge(thing['things_keys']['thing'], thing['weapon']['ammo']['things_keys']['thing'], 3)

    self._graphviz.render()
