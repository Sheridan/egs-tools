import pprint
from rich import print as rprint
from empyrion.model.dialogs import CDialogs
from empyrion.translate.translate import CTranslate
from empyrion.helpers.strings import text_for_context


class CTranslateDialogs(CTranslate):
  def __init__(self):
    super().__init__('dialogues')
    self._excluded_from_context = {'str': [], 'substr': []}
    self._buildExcludedFromContext()

  def _buildExcludedFromContext(self):
    self._excluded_from_context['substr'] = ['(back)', '(leave)', '>Back<', '>Leave<', 'Confirm Order (', 'Register (']
    for ex in ['Exit', 'Leave', 'Back', 'Set', 'Cancel', 'Continue', 'Clear', 'Yes', 'No', 'Maybe', 'Log off', 'Goodbye', 'Confirm']:
      for ex_variant in [ex, f"{ex}.", ex.lower(), ex.capitalize(), ex.upper(), ex.title()]:
        self._excluded_from_context['str'].append(ex_variant)

  def _loadTexts(self, key_name, keys):
    result = {}
    i = 0
    for key in keys:
      src_text = text_for_context(self._translation.get_src_language(key))
      if (all(sub not in src_text for sub in self._excluded_from_context['substr']) and
          src_text not in self._excluded_from_context['str'] and
          src_text not in result.values()):
        result[f'{key_name} {i}'] = src_text
        i += 1
    return result

  def _makeContextData(self, dialog):
    return {
      'phrases': self._loadTexts('phrase', dialog['phrases']),
      'npc': self._loadTexts('npc name', dialog['npc'])
    }

  def _translateDialog(self, dialog):
    context = self._makeContextData(dialog)
    for group in ['npc', 'phrases']:
      for key in dialog[group]:
        self._translateOne(f"dialog {group}", key, context)

  def _totalPhrases(self, dialogs):
    tp = set()
    for dialog in dialogs:
      for group in ['npc', 'phrases']:
        tp.update(dialog[group])
    return len(tp)

  def translate(self):
    dialogs = CDialogs().dialogs()
    self._setTotalStrings(self._totalPhrases(dialogs))
    for dialog in dialogs:
      self._translateDialog(dialog)
    self._translation.save()
