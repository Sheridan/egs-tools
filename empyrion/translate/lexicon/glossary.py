import re
from empyrion.translate.lexicon.lexicon import CLexicon

class CGlossary(CLexicon):
  def __init__(self):
    super().__init__("glossary")
    self._insignificant_words = ['the', 'and', 'block', 'blocks', 'space', 'light', 'hard']
    self._re_cache = {}

  # def _build(self):


  def _isInsignificantWord(self, word):
    if len(word) < 3:
      return True
    return word.lower() in self._insignificant_words

  def _wordInText(self, word, text):
    if word not in self._re_cache:
      self._re_cache[word] = re.compile(r'(?<!\w)' + re.escape(word) + r'(?!\w)')
    return self._re_cache[word].search(text)

  def filter(self, text):
    filtered = {}
    cleaned = self._cleanText(text)
    for group in self._data:
      for key, value in self._data[group].items():
        if self._wordInText(key.lower(), cleaned):
          filtered[key] = value
          continue
        for key_word in key.lower().split():
          if not self._isInsignificantWord(key_word) and self._wordInText(key_word, cleaned):
            filtered[key] = value
    return filtered

  def isGlossaryPhrase(self, text):
    cleaned = self._cleanText(text)
    for group in self._data:
      for key in self._data[group]:
        if self._data[group][key].lower() == cleaned:
          return True
    return False

  def untranslatedEntryes(self, text):
    text = text.lower()
    result = set()
    for group in self._data:
      for key, value in self._data[group].items():
        lkey = key.lower()
        if self._wordInText(lkey, text) and lkey != value.lower():
          result.add(key)
    return sorted(result)

glossary = CGlossary()
