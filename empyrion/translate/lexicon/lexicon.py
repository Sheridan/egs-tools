import json
from empyrion.options import options
from empyrion.helpers.strings import text_for_translate

class CLexicon:
  def __init__(self, book):
    self._data = self._load(book)

  def _load(self, path):
    with open(f'context/{path}/{options.get("translation.dst_language", "Russian")}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

  def _cleanText(self, text):
    return text_for_translate(text.lower())
