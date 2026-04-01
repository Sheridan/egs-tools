import yaml
import json
import random
from empyrion.options import options
from rich import print as rprint
import empyrion.helpers.color as clr

class CPda:
  def __init__(self):
    self._filename = options.get("conf_path", 'data') + "/Extras/PDA/PDA.yaml"

  def _load(self):
    rprint(clr.loadf(self._filename))
    with open(self._filename, 'r') as file:
      return yaml.safe_load(file)

  def _extractValues(self, complex_value):
    values = []
    if '|' in complex_value:
      splitted = complex_value.split('|')
      for part in splitted:
        if ';' in part or part.strip() == '':
          continue
        elif 'pda_' in part.lower():
          values.append(part.strip())
    return values

  def _loadMessages(self, group):
    messages = []
    for name in ['StartMessage', 'CompletedMessage']:
      if self._keyExists(group, name):
        messages += self._extractValues(group[name])
    return messages

  def _keyExists(self, group, key):
    exists = key in group and group[key]
    if exists:
      if   isinstance(group[key], list):
        exists = len(group[key]) > 0
      elif isinstance(group[key], str):
        exists = group[key].strip() != ''
    return exists

  def _loadTaskAction(self, action):
    result = {}
    if self._keyExists(action, 'ActionTitle'):
      result['title'] = action['ActionTitle']
    if self._keyExists(action, 'Description'):
      result['description'] = action['Description']
    if self._keyExists(action, 'StartMessage') or self._keyExists(action, 'CompletedMessage'):
      result['messages'] = self._loadMessages(action)
    return result

  def _loadCTask(self, task):
    result = {}
    if self._keyExists(task, 'TaskTitle'):
      result['title'] = task['TaskTitle']
    if self._keyExists(task, 'StartMessage') or self._keyExists(task, 'CompletedMessage'):
      result['messages'] = self._loadMessages(task)
    if self._keyExists(task, 'Actions'):
      result['actions'] = []
      for action in task['Actions']:
        result['actions'].append(self._loadTaskAction(action))
    return result

  def _loadChapter(self, chapter):
    result = {}
    if self._keyExists(chapter, 'ChapterTitle'):
      result['title'] = chapter['ChapterTitle']
    if self._keyExists(chapter, 'Category'):
      result['category'] = chapter['Category']
    if self._keyExists(chapter, 'Group'):
      result['group'] = chapter['Group']
    if self._keyExists(chapter, 'StartMessage') or self._keyExists(chapter, 'CompletedMessage'):
      result['messages'] = self._loadMessages(chapter)
    if self._keyExists(chapter, 'Tasks'):
      result['tasks'] = []
      for task in chapter['Tasks']:
        result['tasks'].append(self._loadCTask(task))
    return result

  def pda(self):
    pda_data = self._load()
    chapters = []
    for chapter in pda_data['Chapters']:
      chapters.append(self._loadChapter(chapter))
    with open("trash/pda.json", "w", encoding="utf-8") as f:
      json.dump(chapters, f, ensure_ascii=False, indent=4)
    # if options.get("debug", False):
    #   random.shuffle(chapters)
    return chapters
    # rprint(pda_data)
