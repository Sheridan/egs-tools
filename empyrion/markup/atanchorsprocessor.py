import re
from empyrion.markup.processor import CProcessor

class CAtAnchorsProcessor(CProcessor):
  def __init__(self):
    super().__init__()
    self._re = re.compile(r'@[a-zA-Z]+\d+')

  def extract(self, text):
    return sorted(self._re.findall(text))

  def _getDifferenceString(self, missing_aa, extra_aa):
    result = []
    if len(missing_aa) > 0:
      result.append(f'Missing anchors: {', '.join(missing_aa)}. Insert the missing anchors into the translation at their exact original positions.')
    if len(extra_aa) > 0:
      result.append(f'Extra anchors: {', '.join(extra_aa)}. Remove these anchors from the translation. They must not appear in the output.')
    return '; '.join(result)

  def _compare(self, original, translated):
    original_aa = self.extract(original)
    translated_aa = self.extract(translated)
    missing_aa = set()
    extra_aa = set()
    for ph in original_aa:
      if ph not in translated_aa:
        missing_aa.add(ph)
    for ph in translated_aa:
      if ph not in original_aa:
        extra_aa.add(ph)
    if len(missing_aa) > 0 or len(extra_aa) > 0:
      return False, self._getDifferenceString(missing_aa, extra_aa)
    return True, ''

  def exists(self, text: str) -> bool:
    return self._re.search(text) is not None

  def removeAtAnchors(self, text):
    return self._re.sub('', text).strip()

atanchors_processor = CAtAnchorsProcessor()
