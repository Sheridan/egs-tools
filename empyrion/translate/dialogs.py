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

  def _makeContextData(self, dialog):
    context = {'all_dialog_phrases': {}, "npc": {}}
    if 'npc_name' in dialog:
      npc_name_key = dialog['npc_name']
      if self._translation.exists(npc_name_key):
        context['npc']['name'] = text_for_context(self._translation.get_src_language(npc_name_key))
      else:
        context['npc']['name'] = 'Unknown'
    else:
      context['npc']['name'] = 'Unknown'
    phrase_num = 0
    for key in dialog['phrases_keys']:
      if self._translation.exists(key):
        src_text = self._translation.get_src_language(key)
        if (all(sub not in src_text for sub in self._excluded_from_context['substr']) and
            src_text not in self._excluded_from_context['str']):
          context['all_dialog_phrases'][f'phrase_{phrase_num}'] = text_for_context(src_text)
          phrase_num += 1
    # pprint.pprint(context)
    return context

  def _translateNPCName(self, dialog, context):
    if 'npc_name' not in dialog:
      return
    npc_name_key = dialog['npc_name']
    self._translateOne("dialog NPC name", npc_name_key, context)

  def _translateDialog(self, dialog):
    context = self._makeContextData(dialog)
    self._translateNPCName(dialog, context)
    for key in dialog['phrases_keys']:
      self._translateOne("dialog", key, context)

  def _totalPhrases(self, dialogs):
    tp = 0
    for dialog in dialogs:
      tp += len(dialog['phrases_keys'])
      if 'npc_name' in dialog:
        tp += 1
    return tp

  def translate(self):
    dialogs = CDialogs().dialogs()
    self._setTotalStrings(self._totalPhrases(dialogs))
    for dialog in dialogs:
      self._translateDialog(dialog)
    self._translation.save()
    # pprint.pprint(dialogs)
