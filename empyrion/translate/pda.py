import pprint
import re
from rich import print as rprint
from empyrion.model.pda import CPda
from empyrion.translate.translate import CTranslate
from empyrion.state.state import state
from empyrion.helpers.strings import text_for_context, is_untranslated_string

class CTranslatePda(CTranslate):
  def __init__(self):
    super().__init__('pda')

  def _translatePdaOne(self, what, key, context):
    text = self._translation.get_src_language(key)
    if is_untranslated_string(text):
      rprint(f'{self._translationProgress()} [green]{what} [bold]{key}[/bold] no need translation[/green]')
      self._incrementTranslated()
      state.appendTranslateState(self._translation_file, key, text)
    self._translateOne(what, key, context)

  def _context(self, title, group):
    context = {f'{title}': {} }
    if 'category' in group:
      context[f'{title}']['category'] = group['category']
    if 'group' in group:
      context[f'{title}']['group'] = text_for_context(self._translation.get_src_language(group['group']))
    if 'title' in group:
      context[f'{title}']['title'] = text_for_context(self._translation.get_src_language(group['title']))
    if 'messages' in group:
      i = 0
      for message in group['messages']:
        context[f'{title}'][f'message {i}'] = text_for_context(self._translation.get_src_language(message))
        i += 1
    return context

  def _translateAction(self, task_context, action):
    action_context = task_context | self._context('action', action)
    if 'title' in action and self._translation.exists(action['title']):
      self._translatePdaOne("action title", action['title'], action_context)
    if 'description' in action and self._translation.exists(action['description']):
      self._translatePdaOne("action description", action['description'], action_context)
    if 'messages' in action:
      for message in action['messages']:
        self._translatePdaOne("action message", message, action_context)

  def _translateTask(self, chapter_context, task):
    task_context = chapter_context | self._context('task', task)
    if 'title' in task and self._translation.exists(task['title']):
      self._translatePdaOne("chapter title", task['title'], task_context)
    if 'messages' in task:
      for message in task['messages']:
        self._translatePdaOne("chapter message", message, task_context)
    if 'actions' in task:
      for action in task['actions']:
        self._translateAction(task_context, action)

  def _translateChapter(self, chapter):
    chapter_context = self._context('chapter', chapter)
    if 'title' in chapter and self._translation.exists(chapter['title']):
      self._translatePdaOne("chapter title", chapter['title'], chapter_context)
    if 'group' in chapter and self._translation.exists(chapter['group']):
      self._translatePdaOne("chapter group", chapter['group'], chapter_context)
    if 'messages' in chapter:
      for message in chapter['messages']:
        self._translatePdaOne("chapter message", message, chapter_context)
    if 'tasks' in chapter:
      for task in chapter['tasks']:
        self._translateTask(chapter_context, task)

  def _countStrings(self, pda):
    count = 0
    for chapter in pda:
      if 'title'    in chapter: count += 1
      if 'group'    in chapter: count += 1
      if 'messages' in chapter: count += len(chapter['messages'])
      if 'tasks' in chapter:
        for task in chapter['tasks']:
          if 'title'    in task: count += 1
          if 'messages' in task: count += len(task['messages'])
          if 'action' in task:
            for action in task['action']:
              if 'title'       in action: count += 1
              if 'description' in action: count += 1
              if 'messages'    in action: count += len(action['messages'])
    return count

  def translate(self):
    pda = CPda().pda()
    self._setTotalStrings(self._countStrings(pda))
    for chapter in pda:
      self._translateChapter(chapter)
    # rprint(pda)
