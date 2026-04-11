import re
import sys
import pprint
from empyrion.translate.lexicon.lexicon import CLexicon
from empyrion.helpers.strings import no_letters

class CGlossary(CLexicon):
  def __init__(self):
    super().__init__("glossary")
    self._re_cache = {}
    self._flat = {}
    self._flattern()

  def _flattern(self):
    for group in self._data['glossary']:
      for key, value in self._data['glossary'][group].items():
        if key in self._flat:
          sys.exit(f"Duplicated key '{key}' in glossary")
        self._flat[key] = value
    # pprint.pprint(self._flat)

  def _isUntranslable(self, text):
    if no_letters(self._cleanText(text)):
      return True
    for part in self._data['untranslable']:
      if part in text:
        return True
    return False

  def _isInsignificantWord(self, word):
    if len(word) < 3:
      return True
    return word.lower() in self._data['insignificant_words']

  def _wordInText(self, word, text):
    if word not in self._re_cache:
      self._re_cache[word] = re.compile(r'(?<!\w)' + re.escape(word) + r'(?!\w)')
    return self._re_cache[word].search(text)

  def filter(self, text):
    filtered = {}
    cleaned = self._cleanText(text)
    cleaned_lower = cleaned.lower()
    for key, value in self._flat.items():
      if self._wordInText(key.lower(), cleaned_lower):
        filtered[key] = value
        continue
      for key_word in key.lower().split():
        if not self._isInsignificantWord(key_word) and self._wordInText(key_word, cleaned_lower):
          filtered[key] = value
    return filtered

  def isGlossaryPhrase(self, text):
    cleaned = self._cleanText(text)
    for key in self._flat:
      if self._flat[key].lower() == cleaned.lower():
        return True
    return False

  def untranslatedEntryes(self, text):
    cleaned = self._cleanText(text).lower()
    result = set()
    for key, value in self._flat.items():
      lkey = key.lower()
      if self._wordInText(lkey, cleaned) and lkey != value.lower():
        result.add(key)
    return sorted(result)

  def tryHardcode(self, s):
    if s in self._data['hardcode']:
      return self._data['hardcode'][s]
    return None

glossary = CGlossary()
