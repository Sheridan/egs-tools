from empyrion.markup.processor import CProcessor

class CPlaceholdersProcessor(CProcessor):
  def __init__(self):
    super().__init__()

  def extract(self, text):
    result = []
    start = None
    depth = 0

    for i, ch in enumerate(text):
      if ch == '{':
        if depth == 0:
          start = i  # начало нового плейсхолдера
        depth += 1
      elif ch == '}':
        if depth > 0:
          depth -= 1
          if depth == 0 and start is not None:
            result.append(text[start:i+1])
            start = None
    return list(result)

  def _getDifferenceString(self, missing_ph, extra_ph):
    result = []
    if len(missing_ph) > 0:
      result.append(f'Missing placeholders: {', '.join(missing_ph)}')
    if len(extra_ph) > 0:
      result.append(f'Extra placeholders: {', '.join(extra_ph)}')
    return '; '.join(result)

  def _compare(self, original, translated):
    original_ph = self.extract(original)
    translated_ph = self.extract(translated)
    missing_ph = set()
    extra_ph = set()
    for ph in original_ph:
      if ph not in translated_ph:
        missing_ph.add(ph)
    for ph in translated_ph:
      if ph not in original_ph:
        extra_ph.add(ph)
    if len(missing_ph) > 0 or len(extra_ph) > 0:
      return False, self._getDifferenceString(missing_ph, extra_ph)
    return True, ''

  def exists(self, text: str) -> bool:
    start = text.find('{')
    if start == -1:
      return False
    return text.find('}', start + 1) != -1

placeholders_processor = CPlaceholdersProcessor()
