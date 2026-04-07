
import copy
from empyrion.translate.lexicon.lexicon import CLexicon

class CCharacters(CLexicon):
  def __init__(self):
    super().__init__("characters")

  def _getCharacter(self, character):
    result = copy.deepcopy(character)
    if 'group' in result:
      result['characteristic'] += self._data['groups'][result['group']]['characteristic']
    return result

  def filter(self, text, object_context):
    filtered = {}
    cleaned = self._cleanText(text)
    for key in self._data['characters']:
      character = self._getCharacter(self._data['characters'][key])

      for text_word in cleaned.split(' '):
        if text_word != '' and text_word in character['keywords'] and key not in filtered:
          filtered[key] = character

      if 'npc' in object_context:
        for _,npc in object_context['npc'].items():
          for key_word in character['keywords']:
            if key_word.lower() in npc.lower().strip() and key not in filtered:
              filtered[key] = character

    # print(object_context)
    # print(filtered)
    return filtered

characters = CCharacters()
