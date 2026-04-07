import re
from empyrion.markup.processor import CProcessor

class CTagsProcessor(CProcessor):
  def __init__(self):
    super().__init__()
    # self._tags_re =  re.compile(r'/?([aiubc-]|su[bp]|color|url|#?[a-fA-F0-9]{6})')
    self._re =  re.compile(r'[\[<]/?([aiubc-]|su[bp]|color(=#?[a-fA-F0-9]{6})?|url(=.+?)?|#?[a-fA-F0-9]{6})[>\]]')

  def _allowedTagsSkips(self, n):
    return 0
    if n >=  4 and n <  8: return 1
    if n >=  8 and n < 16: return 2
    if n >= 16 and n < 20: return 3
    if n >= 20:            return 4
    return 0


  def _searchUnknownTags(self, translated_tags):
    pass

  def _getDifferenceString(self, original_tags, translated_tags):
    return ', '.join([x for x in original_tags if x not in translated_tags])
    # return ', '.join(list(set(original_tags) - set(translated_tags)))

  def _compare(self, original, translated):
    original_tags  = self.extract(original)
    translated_tags = self.extract(translated)
    if original_tags != translated_tags:
      allowed_skip = self._allowedTagsSkips(len(original_tags))
      if allowed_skip == 0 or abs(len(original_tags) - len(translated_tags)) > allowed_skip:
        if len(set(original_tags) - set(translated_tags)) > 0:
          return False, f'Some tags from the original text are missing: {self._getDifferenceString(original_tags, translated_tags)}'
        if len(set(translated_tags) - set(original_tags)) > 0:
          return False, f'Some extra tags in translated text: {self._getDifferenceString(translated_tags, original_tags)}'
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
