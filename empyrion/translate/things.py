import pprint
from rich import print as rprint
from empyrion.translate.translate import CTranslate
from empyrion.model.things import things
from empyrion.helpers.strings import text_for_context

class CTranslateThings(CTranslate):
  def __init__(self):
    super().__init__('localization')
    self._already_sheduled = []

  def _makeContextData(self, thing):
    context = {'metadata': {}, 'labels': {}}
    for option in ['Name', 'Material', 'Class', 'Shape', 'Group', 'RecipeName', 'Category', 'IndexName', 'EnergyDynamicGroup', 'Info', 'PickupTarget', 'TemplateRoot', 'SizeInBlocksLocked']:
      if option in thing['merged'] and thing['merged'][option]:
        value = thing['merged'][option]
        if 'value' in thing['merged'][option]:
          value = thing['merged'][option]['value']
        context['metadata'][option] = value
    if thing['icon'] != 'Eden_DummyRE':
      context['metadata']['icon'] = thing['icon']
    if 'labels' in thing and thing['labels']:
      for lkey in ['caption', 'description']:
        if lkey in thing['labels'] and thing['labels'][lkey]:
          context['labels'][lkey] = text_for_context(thing['labels'][lkey])
    return context

  def _translateThing(self, thing, what):
    key = thing['labels']['labels_keys'][what]
    if key in self._already_sheduled:
      return
    self._translateOne(f"thing {what}", key, self._makeContextData(thing))
    self._already_sheduled.append(key)

  def _totalPhrases(self, things):
    tp = 0
    for thing in things:
      if 'labels' in thing and thing['labels']:
        if 'labels_keys' in thing['labels'] and thing['labels']['labels_keys']:
          for what in ['caption', 'description']:
            if what in thing['labels']['labels_keys'] and thing['labels']['labels_keys'][what]:
              tp += 1
    return tp

  def translate(self):
    loaded_things = things.things(True)
    self._setTotalStrings(self._totalPhrases(loaded_things))
    for thing in loaded_things:
      if thing['labels']:
        # pprint.pprint(thing)
        for what in ['caption', 'description']:
          self._translateThing(thing, what)
    self._translation.save()
