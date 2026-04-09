import re

from empyrion.markup.processor import CProcessor
from empyrion.helpers.strings import quoted_list
from empyrion.helpers.lists import list_difference

class CTagsProcessor(CProcessor):
  def __init__(self):
    super().__init__()
    # self._tags_re =  re.compile(r'/?([aiubc-]|su[bp]|color|url|#?[a-fA-F0-9]{6})')
    self._re =  re.compile(r'[\[<]/?([aiubc-]|su[bp]|size(=[0-9]+%?)?|color(=#?[a-fA-F0-9]{6})?|url(=.+?)?|#?[a-fA-F0-9]{6})[>\]]')

  def _compare(self, original, translated):
    original_tags  = self.extract(original)
    translated_tags = self.extract(translated)
    if original_tags != translated_tags:
      if len(original_tags) > len(translated_tags):
        return False, f'Missing tags: {quoted_list(list_difference(original_tags, translated_tags))}. Restore all tags from the source text exactly where they appear.'
      if len(original_tags) < len(translated_tags):
        return False, f'Extra tags: {quoted_list(list_difference(translated_tags, original_tags))}. Remove any tags not present in the source text. Keep only the exact tags from the original.'
    return True, ''


  def removeTags(self, text: str) -> str:
    return self._re.sub('', text).strip()

  def tagsList(self, text):
    tags = list(set(self.extract(text)))
    tags.sort(reverse=True)
    return tags

  def extract(self, s: str) -> list:
    return [m.group(0) for m in self._re.finditer(s)]

  def exists(self, text: str) -> bool:
    return self._re.search(text) is not None

tags_processor = CTagsProcessor()
