
from empyrion.translate.lexicon.lexicon import CLexicon

class CGlossary(CLexicon):
  def __init__(self):
    super().__init__("glossary")

  def _isInsignificantWord(self, word):
    if len(word) < 3:
      return True
    return word.lower() in ['the', 'and', 'block', 'blocks', 'space', 'light', 'hard']

  def filter(self, text):
    filtered = {}
    cleaned = self._cleanText(text)
    for group in self._data:
      for key in self._data[group]:
        if key.lower() in cleaned:
          filtered[key] = self._data[group][key]
          continue
        for key_word in key.lower().split():
          if not self._isInsignificantWord(key_word) and key_word in cleaned:
            filtered[key] = self._data[group][key]
    return filtered

  def isGlossaryPhrase(self, text):
    cleaned = self._cleanText(text)
    for group in self._data:
      for key in self._data[group]:
        if self._data[group][key].lower() == cleaned:
          return True
    return False
