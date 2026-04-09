import random
from rich import print as rprint
from empyrion.options import options
from empyrion.datasource.datasource import datasource
import empyrion.helpers.color as clr

class CDialogs:
  def __init__(self):
    self._datasource = datasource['ds_dialogues']
    self._localisation = datasource['dialogues']
    self._meaningful_names = ['BarkingState', 'Input', 'Next', 'Option', 'OptionNext', 'Output']
    self._dialogs = {}

  def _loadValues(self, raw_value):
    if isinstance(raw_value, dict):
      values = []
      if raw_value['value'] not in values:
        values.append(raw_value['value'])
      name_index = 1
      while True:
        name_variant = f'param{name_index}'
        if name_variant in raw_value:
          val = raw_value[name_variant]
          if val not in values:
            values.append(val)
          name_index += 1
          continue
        return values
    return [raw_value]

  def _loadDialogValueNameVariants(self, raw, value_name):
    if value_name in raw:
      return [value_name]
    variants = []
    variant_index = 1
    while True:
      variant_name = f'{value_name}_{variant_index}'
      if variant_name in raw:
        variants.append(variant_name)
        variant_index += 1
        continue
      break
    return variants

  def _loadDialogValues(self, raw):
    values = []
    for value_name in self._meaningful_names:
      for variant_name in self._loadDialogValueNameVariants(raw, value_name):
        for v in self._loadValues(raw[variant_name]):
          if v not in values:
            values.append(v)
    return values

  def _loadDialog(self, key):
    rprint(f'[green]Loading dialog {clr.key(key)}[/green]')
    dialog = {'key': key, 'childs': [], 'phrases': [], 'parents': [], 'npc': []}
    raw = self._datasource.get(key)
    for value in self._loadDialogValues(raw):
      if self._datasource.exists(value):
        if value not in dialog['childs']:
          dialog['childs'].append(value)
      elif self._localisation.exists(value):
        if value not in dialog['phrases']:
          dialog['phrases'].append(value)
    if 'NPCName' in raw and self._localisation.exists(raw['NPCName']):
      if raw['NPCName'] not in dialog['npc']:
        dialog['npc'].append(raw['NPCName'])
    return dialog

  def _loadDialogs(self):
    for key in sorted(self._datasource.keys()):
      self._dialogs[key] = self._loadDialog(key)

  def _bageRoots(self):
    rprint(f'[green]Finding root dialogs[/green]')
    for _, dialog in sorted(self._dialogs.items()):
      for child in dialog['childs']:
        self._dialogs[child]['parents'].append(dialog['key'])

  def _flatDialog(self, root, visited):
    dialog = {'root': root['key'], 'keys': [root['key']], 'phrases': list(root['phrases']), 'npc': list(root['npc'])}
    for child in root['childs']:
      if child not in visited:
        visited.add(child)
        c_root = self._flatDialog(self._dialogs[child], visited)
        for pkey in ['phrases', 'npc', 'keys']:
          for item in c_root[pkey]:
            if item not in dialog[pkey]:
              dialog[pkey].append(item)
    return dialog

  def _rootDialogs(self):
    rprint(f'[green]Extract root dialogs[/green]')
    roots = []
    for _, dialog in sorted(self._dialogs.items()):
      if len(dialog['parents']) == 0:
        dialog = self._flatDialog(dialog, set())
        if len(dialog['phrases']) > 0:
          roots.append(dialog)
    return roots

  def rootDialogs(self):
    self._loadDialogs()
    self._bageRoots()
    dialogs = self._rootDialogs()
    if options.get("debug", False) and options.get("random_shuffle_objects", False):
      random.shuffle(dialogs)
    return dialogs
