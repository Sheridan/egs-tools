
from rich.live import Live
from rich.table import Table
from rich.markup import escape

from empyrion.datasource.datasource import datasource
from empyrion.state.state import state
from empyrion.state.translationstorage import CTranslationStorage
from empyrion.helpers.strings import replace_literals_newlines_by_newlines

class CView:
  def __init__(self):
    self._storages = {}

  def _storage(self, source):
    if source not in self._storages:
      self._storages[source] = CTranslationStorage(source)
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

  def _loadKeyData(self, ds_name, ds, storage, key):
    return {
      'datasource': ds_name,
      'key'       : key,
      'original'  : replace_literals_newlines_by_newlines(ds.get_src_language(key)),
      'translated': replace_literals_newlines_by_newlines(ds.get_dst_language(key)),
      'stored'    : replace_literals_newlines_by_newlines(storage.get(key))
    }

  def showKey(self, key, rm):
    for name in datasource.datasources('translation'):
      if datasource[name].exists(key):
        if rm:
          self._rmKey(key)
        self._render([self._loadKeyData(name, datasource[name], self._storage(name), key)])
        return

  def showList(self, name):
    if not datasource.exists('translation', name):
      print(f'Unknown datasource. Known list: {', '.join(datasource.datasources('translation'))}')
      return

    records = []
    for key in datasource[name].keys():
      records.append(self._loadKeyData(name, datasource[name], self._storage(name), key))
    self._render(records)

  def search(self, s, rm):
    records = []
    for name in datasource.datasources('translation'):
      for key in datasource[name].keys():
        record = self._loadKeyData(name, datasource[name], self._storage(name), key)
        if s in key:
          if rm:
            self._rmKey(key)
          records.append(self._loadKeyData(name, datasource[name], self._storage(name), key))
          continue
        if s in record['original']:
          if rm:
            self._rmKey(key)
          records.append(self._loadKeyData(name, datasource[name], self._storage(name), key))
          continue
        if s in record['translated']:
          if rm:
            self._rmKey(key)
          records.append(self._loadKeyData(name, datasource[name], self._storage(name), key))
          continue
        if s in record['stored']:
          if rm:
            self._rmKey(key)
          records.append(self._loadKeyData(name, datasource[name], self._storage(name), key))
          continue
    self._render(records)

  def _rmKey(self, key):
    for name in datasource.datasources('translation'):
      if datasource[name].exists(key):
        state.rmTranslatedByKey(name, key)
        self._storage(name).rm(key)
        state.save()
        self._storage(name).save()
