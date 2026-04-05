from rich.console import Console
from rich.markup import escape
from rich.table import Table

from empyrion.jsonstorage import CJsonStorage

class CState(CJsonStorage):
  def __init__(self):
    super().__init__('trash/state.json')

  def setStringsTotal(self, source, total):
    self._set('totals', 'strings', source, total)

  def incrementTranslatedStrings(self, source):
    self._set('processing', 'strings', source, self._last('processing', 'strings', source, 0) + 1)

  def appendTranslateState(self, hasher):
    self._set('translation', hasher.group(), hasher.key(), hasher.hash())

  def keyIsTranslated(self, source, key):
    section = self._section('translation', source)
    if section is None:
      return False
    for stored_key in section:
      if key in stored_key:
        return True
    return False

  def isTranslated(self, hasher):
    section = self._section('translation', hasher.group())
    if section is None:
      return False
    if hasher.key() not in section:
      return False
    # print(f'-------------- {hasher.group()}|{hasher.key()}: {section[hasher.key()]} =? {hasher.hash()} --------------')
    return section[hasher.key()] == hasher.hash()

  def isDuplicateKey(self, source, key):
    section = self._section('duplicates', 'translation')
    if section is None:
      return False
    if source not in section:
      return False
    return key in section[source]

  def appendDuplicateKey(self, source, key):
    self._add('duplicates', 'translation', source, key)

  def rmDuplicateKey(self, source, key):
    section = self._section('duplicates', 'translation')
    if section is not None and source in section:
      section[source].remove(key)

  def clearDuplicates(self):
    if self._tool('duplicates') is not None:
      del self._data['duplicates']

  def appendOwnedKey(self, source, key):
    self._add('owned', 'translation', source, key)

  def isOwnedKey(self, source, key):
    section = self._section('owned', 'translation')
    if section is None:
      return False
    if source not in section:
      return False
    return key in section[source]

  def getStringsCounts(self, source):
    return  {
              'total': self._last('totals', 'strings', source, 0),
              'processed': self._last('processing', 'strings', source, 0),
            }

  def showKnownKeysTranslateState(self):
    translation = self._tool('translation')
    duplicates = self._section('duplicates', 'translation')
    if translation is None:
      return
    total_hashes = 0
    total_duplicates = 0
    total_strings = 0
    total_processed_strings = 0
    table = Table(title="Translate process", expand=True)
    table.add_column("Source"           , style="yellow"        , no_wrap=False)
    table.add_column("Hashes"           , style="magenta"       , no_wrap=False)
    table.add_column("Duplicates"       , style="cyan"          , no_wrap=False)
    table.add_column("Processed strings", style="dark_goldenrod", no_wrap=False)
    table.add_column("Total strings"    , style="dark_violet"   , no_wrap=False)
    for section_name in translation:
      hashes_len = len(translation[section_name])
      duplicates_len = 0
      if duplicates is not None and section_name in duplicates:
        duplicates_len = len(duplicates[section_name])
      section_strings = self._last('totals', 'strings', section_name, 0)
      section_processed_strings = self._last('processing', 'strings', section_name, 0)
      table.add_row(section_name, str(hashes_len), str(duplicates_len), str(section_processed_strings), str(section_strings))
      total_hashes += hashes_len
      total_duplicates += duplicates_len
      total_strings += section_strings
      total_processed_strings += section_processed_strings
    table.add_row('Total', str(total_hashes), str(total_duplicates), str(total_processed_strings), str(total_strings))
    Console().print(table)



state = CState()
