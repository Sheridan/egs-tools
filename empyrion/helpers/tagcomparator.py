
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.pretty import Pretty
from empyrion.options import options

class TagComparator:
  def __init__(self, original_string: str):
    self.original_tags = self._extract_tags(original_string)

  def compare(self, other_string: str) -> bool:
    other_tags = self._extract_tags(other_string)
    if self.original_tags != other_tags:
      self._show(self.original_tags, other_tags)
      return False
    return True

  def _show(self, original, current):
    if options.get("debug", False):
      if len(original) > 0 or len(current) > 0:
        table = Table(show_lines=True, expand=True)
        table.add_column("Original" , style="magenta", no_wrap=False, highlight=False)
        table.add_column("Current", style="yellow" , no_wrap=False, highlight=False)
        table.add_row(Pretty(original, indent_size=2), Pretty(current, indent_size=2))
        table.add_row(str(len(original)), str(len(current)))
        Console().print(table)

  def _extract_tags(self, s: str):
    tags = []
    i = 0
    n = len(s)
    while i < n:
      if s[i] == '<' and s[i+1] != ' ':
        j = s.find('>', i)
        if j != -1:
          tags.append(s[i:j+1])
          i = j + 1
        else:
          i += 1
      elif s[i] == '[' and s[i+1] != ' ':
        j = s.find(']', i)
        if j != -1:
          tags.append(s[i:j+1])
          i = j + 1
        else:
          i += 1
      else:
        i += 1
    return tags
