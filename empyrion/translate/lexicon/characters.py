
from empyrion.translate.lexicon.lexicon import CLexicon

class CCharacters(CLexicon):
  def __init__(self):
    super().__init__("characters")

  def filter(self, text, object_context):
    filtered = {}
    cleaned = self._cleanText(text)
    for key in self._data['characters']:
      character = self._data['characters'][key]

      for text_word in cleaned.split(' '):
        if text_word != '' and text_word in character['keywords']:
          if key not in filtered:
            filtered[key] = character

      if 'npc' in object_context:
        for npc in object_context['npc']:
          if npc.lower().strip() in character['keywords']:
            if key not in filtered:
              filtered[key] = character

    return filtered
