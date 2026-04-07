
from rich.console import Console
from rich.table import Table
from rich.pretty import Pretty
from rich.markup import escape
from empyrion.options import options

class CProcessor:
  def __init__(self):
    pass

  def compare(self, original, translated):
    rc, message = self._compare(original, translated)
    if not rc:
      self._show(original, translated, message)
    return rc, message

  def _show(self, original, translated, message):
    if options.get("debug", False):
      original_list  = self.extract(original)
      translated_list = self.extract(translated)
      if len(original_list) > 0 or len(translated_list) > 0:
        table = Table(title=escape(message), show_lines=True, expand=True)
        table.add_column("Original"  , style="magenta", no_wrap=False, highlight=False)
        table.add_column("Translated", style="yellow" , no_wrap=False, highlight=False)
        table.add_row(Pretty(original_list, indent_size=2), Pretty(translated_list, indent_size=2))
        table.add_row(str(len(original_list))             , str(len(translated_list)))
        Console().print(table)
