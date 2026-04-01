import json
from empyrion.options import options
from empyrion.helpers.strings import text_for_translate
from rich import print as rprint
import empyrion.helpers.color as clr

class CLexicon:
  def __init__(self, book):
    self._data = self._load(book)

  def _load(self, path):
    fn = f'{path}/{options.get("translation.dst_language", "Russian")}.json'
    rprint(clr.loadf(fn))
    with open(f'context/{fn}', 'r', encoding='utf-8') as f:
        return json.load(f)

  def _cleanText(self, text):
    return text_for_translate(text.lower())
