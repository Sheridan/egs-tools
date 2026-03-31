import json
import pprint
import random
from rich import print as rprint
from empyrion.options import options
from empyrion.datasource.datasource import datasource

class CDialogs:
  def __init__(self):
    self._dialogues = datasource['ds_dialogues']
    self._loaded_dialogs_keys = set()
    self._flag_values =  ['End', 'Return']

  def _extractOptionValues(self, raw, option_name):
    values = []
    if isinstance(raw[option_name], dict):
      value = raw[option_name]['value']
      if value not in self._flag_values:
        values.append(value)
      value_index = 1
      while True:
        value_option_name = f"param_{value_index}"
        if value_option_name in raw[option_name]:
          if value not in self._flag_values:
            values.append(value)
        else:
          break
        value_index += 1
    else:
      value = raw[option_name]
      if value not in self._flag_values:
        values.append(value)
    return values

  def _loadDialogOptions(self, raw):
    options = []
    for option_prefix in ['OptionNext', 'Option', 'Next', 'Output', 'BarkingState', 'Input']:
      if option_prefix in raw:
        options += self._extractOptionValues(raw, option_prefix)
        continue
      option_index = 1
      while True:
        option_name = f"{option_prefix}_{option_index}"
        if option_name in raw:
          options += self._extractOptionValues(raw, option_name)
        else:
          break
        option_index += 1
    # print(options)
    return options

  def _findNextKey(self, options):
    for option in options:
      if self._dialogues.hasName(option) and option not in self._loaded_dialogs_keys:
        return option
    return None

  def _loadDialog(self, key):
    options = []
    inspect_key = key
    while inspect_key is not None:
      self._loaded_dialogs_keys.add(inspect_key)
      raw = self._dialogues.get(inspect_key)
      options += self._loadDialogOptions(raw)
      inspect_key = self._findNextKey(options)
      if inspect_key is not None:
        options = [item for item in options if item != inspect_key]
      # print(options)
      options = [item for item in options if item not in self._loaded_dialogs_keys]
      # print(self._loaded_dialogs_keys)
    dialog = { 'key': key, 'phrases_keys': list(set(options)) }
    raw = self._dialogues.get(key)
    if 'NPCName' in raw:
      dialog['npc_name'] = raw['NPCName']
    return dialog

  def _showInfo(self, dialogs):
    counter = {
      'actors': set(),
      'phrases': set()
    }
    for dialog in dialogs:
      if 'npc_name' in dialog:
        counter['actors'].add(dialog['npc_name'])
      if 'phrases_keys' in dialog:
        for phrase in dialog['phrases_keys']:
          counter['phrases'].add(phrase)
    print(f"Total dialogs: {len(dialogs)}. Actors: {len(counter['actors'])}. Phrases: {len(counter['phrases'])}. Strings: {len(counter['actors']) + len(counter['phrases'])}")

  def _checkMissing(self, dialogs):
    for key in self._dialogues.names():
      if key not in self._loaded_dialogs_keys:
        print(f'Missing key: {key}')

  def _isRootDialog(self, inspect_key):
    for key in self._dialogues.names():
      for option in self._loadDialogOptions(self._dialogues.get(key)):
        if option == inspect_key:
          return False
    return True

  def dialogs(self):
    dialogs = []
    for key in self._dialogues.names():
      if self._isRootDialog(key):
        print(f'Appending dialog {key}')
        dialogs.append(self._loadDialog(key))
    with open("trash/dialogs.json", "w", encoding="utf-8") as f:
      json.dump(dialogs, f, ensure_ascii=False, indent=4)
    self._checkMissing(dialogs)
    self._showInfo(dialogs)
    # if options.get("debug", False):
    #   random.shuffle(dialogs)
    return dialogs
