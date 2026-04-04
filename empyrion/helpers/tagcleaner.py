import re

class TagCleaner:

  def __init__(self):
    self.patterns = []
    self._definitions = [
        # XML-теги (упрощённый вариант для любых парных тегов)
        (r'<[^>/]+>', r'</[^>]+>'),
        # BBCode (например, [b]...[/b], [i]...[/i])
        (r'\[[a-zA-Z]+\]', r'\[/[a-zA-Z]+\]'),
        # Спецтеги цвета [FFFFFF]...[-]
        (r'\[[A-Fa-f0-9]{6}\]', r'\[-\]'),
        # Спецтеги цвета <color=#000000>...</color>
        (r'<color=#[A-Fa-f0-9]{6}>', r'</color>'),
    ]

  def _buildRe(self):
    for open_pat, close_pat in self._definitions:
      self.patterns.append(re.compile(r'(' + open_pat + r')\s*(' + close_pat + r')', re.DOTALL))



  def clean(self, text: str) -> str:
    if not text:
      return text

    result = text
    changed = True
    while changed:
      changed = False
      for pat in self.patterns:
        new_result, n = pat.subn('', result)
        if n > 0:
          changed = True
          result = new_result
    return result
