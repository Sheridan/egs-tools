import re
from empyrion.translate.lexicon.lexicon import CLexicon

class CExamples(CLexicon):
  def __init__(self):
    super().__init__("examples")
    self._tag_patterns = [
      re.compile(r'\[/?[a-z]+\]', re.DOTALL),
      re.compile(r'</?[a-z]+>'  , re.DOTALL)
    ]

  def _hasTags(self, text):
    for pattern in self._tag_patterns:
      if pattern.search(text):
        return True
    return False

  def filter(self, text):
    filtered = {}
    if self._hasTags(text):
      filtered['tags'] = self._data['tags']
    return filtered
