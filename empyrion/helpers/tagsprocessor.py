import re
from rich.console import Console
from rich.table import Table
from rich.pretty import Pretty
from empyrion.options import options

class CTagsProcessor:
  def __init__(self):
    # self._tags_re =  re.compile(r'/?([aiubc-]|su[bp]|color|url|#?[a-fA-F0-9]{6})')
    self._full_tags_re =  re.compile(r'[\[<]/?([aiubc-]|su[bp]|color(=#?[a-fA-F0-9]{6})?|url(=.+?)?|#?[a-fA-F0-9]{6})[>\]]')

  # def _isTag(self, s):
  #   tag = s[1:-1]
  #   # tag = s
  #   tagname = tag.split('=')[0]
  #   if len(tagname):
  #     return self._tags_re.fullmatch(tagname)
  #   return False

  def _isEven(self, n: int):
    return n % 2 == 0

  def _checkOpenClosedTags(self, tags):
    opens = 0
    closes = 0
    for tag in tags:
      if '/' in tag or '-' in tag:
        closes += 1
      else:
        opens += 1
    return opens == closes

  def compare(self, left, right):
    left_tags  = self._extractTags(left)
    right_tags = self._extractTags(right)
    if left_tags == right_tags:
      return True
    if set(left_tags) == set(right_tags):
      return True
    if abs(len(left_tags) - len(right_tags)) <= 2 and len(left_tags) > 2:
      if self._isEven(len(left_tags)) == self._isEven(len(right_tags)):
        if self._checkOpenClosedTags(left_tags) == self._checkOpenClosedTags(right_tags):
          return True
    self._show(left, right)
    return False

  def _show(self, left, right):
    if options.get("debug", False):
      left_tags  = self._extractTags(left)
      right_tags = self._extractTags(right)
      if len(left_tags) > 0 or len(right_tags) > 0:
        table = Table(show_lines=True, expand=True)
        table.add_column("Original" , style="magenta", no_wrap=False, highlight=False)
        table.add_column("Current", style="yellow" , no_wrap=False, highlight=False)
        table.add_row(Pretty(left_tags, indent_size=2), Pretty(right_tags, indent_size=2))
        table.add_row(str(len(left_tags)), str(len(right_tags)))
        Console().print(table)

  # def test(self, text):
  #   return self._extract_tags(text)

  def removeTags(self, text: str) -> str:
    return self._full_tags_re.sub('', text).strip()

  def tagsList(self, text):
    tags = list(set(self._extractTags(text)))
    tags.sort()
    return tags

  def _extractTags(self, s: str) -> list:
    return [m.group(0) for m in self._full_tags_re.finditer(s)]

  # def _extract_tags(self, s: str):
  #   tags = []
  #   i = 0
  #   n = len(s)
  #   while i < n:
  #     if s[i] == '<':
  #       j = s.find('>', i)
  #       if j != -1:
  #         tag = s[i:j+1]
  #         if self._isTag(tag):
  #           tags.append(tag)
  #         i = j + 1
  #       else:
  #         i += 1
  #     elif s[i] == '[':
  #       j = s.find(']', i)
  #       if j != -1:
  #         tag = s[i:j+1]
  #         if self._isTag(tag):
  #           tags.append(tag)
  #         i = j + 1
  #       else:
  #         i += 1
  #     else:
  #       i += 1
  #   # rprint(tags)
  #   return tags

tags_processor = CTagsProcessor()
