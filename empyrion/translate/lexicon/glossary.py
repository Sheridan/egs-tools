
from empyrion.translate.lexicon.lexicon import CLexicon

class CGlossary(CLexicon):
  def __init__(self):
    super().__init__("glossary")

  def filterByText(self, text):
    filtered = {}
    cleaned = self._cleanText(text)
    for group in self._data.keys():
      for key in self._data[group].keys():
        for key_word in key.lower().split():
          if key_word in cleaned:
            filtered[key] = self._data[group][key]
    return filtered
