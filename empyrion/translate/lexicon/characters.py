
from empyrion.translate.lexicon.lexicon import CLexicon

class CCharacters(CLexicon):
  def __init__(self):
    super().__init__("characters")

  def filterByText(self, text):
    filtered = {}
    cleaned = self._cleanText(text)
    for key in self._data['characters'].keys():
      character = self._data['characters'][key]
      for text_word in cleaned.split(' '):
        if text_word != '' and text_word in character['keywords']:
          filtered[key] = character
    return filtered
