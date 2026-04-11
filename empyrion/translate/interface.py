
from rich.live import Live
from rich.table import Table
from rich.markup import escape

from empyrion.datasource.datasource import datasource
from empyrion.database.state import CStateDB, database
from empyrion.helpers.strings import replace_literals_newlines_by_newlines

class CView:
  def __init__(self):
    self._storages = {}

  def _storage(self, source):
    if source not in self._storages:
      self._storages[source] = datasource[source]
    return self._storages[source]

  def _render(self, records):
    table = Table(expand=True, show_lines=True)
    table.add_column("Datasource\nKey")
    table.add_column("Original")
    table.add_column("Translated")
    table.add_column("In Storage")
    with Live(table, refresh_per_second=1):
      for record in records:
        table.add_row(f'{record['datasource']}\n{record['key']}', escape(record['original']), escape(record['translated']), escape(record['stored']))
    print(f'{len(records)} records')

  def _loadKeyData(self, row):
    return {
      'datasource': row['file'],
      'key'       : row['key'],
      'original'  : replace_literals_newlines_by_newlines(row['original_text']),
      'translated': replace_literals_newlines_by_newlines(self._storage(row['file']).get_dst_language(row['key'])),
      'stored'    : replace_literals_newlines_by_newlines(row['translated_text'])
    }

  def _delete(self, s):
    database.query('delete from translation where original_text like ? or translated_text like ? or key like ?', (f'%{s}%', f'%{s}%', f'%{s}%'))

  def search(self, s, rm):
    s = s.replace('%', '\\%').replace('_', '\\_')
    if rm:
      self._delete(s)
    rows = database.query(f'select file, key, original_text, translated_text from translation where original_text like ? or translated_text like ? or key like ?', (f'%{s}%', f'%{s}%', f'%{s}%'))
    records = []
    for row in rows:
      records.append(self._loadKeyData(row))
    self._render(records)
