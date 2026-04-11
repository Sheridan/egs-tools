from empyrion.database.database import CDatabase
from empyrion.helpers.hasher import CHasher
from rich.console import Console
from rich.markup import escape
from rich.table import Table
from rich import print as rprint
from empyrion.datasource.datasource import datasource

database = CDatabase("trash/progress.db")

class CStateDB:
  def __init__(self, translation_file = None):
    self._translation_file = translation_file
    self._total_strings = {}
    self._create()

  def _create(self) -> None:
    database.query("""
        create table if not exists translation (
            file            text not null,
            key             text not null,
            original_text   text,
            translated_text text,
            context_hash    text,
            PRIMARY KEY (file, key))
    """)
    database.query("""
        create table if not exists metadata (
            file       text not null,
            key        text not null,
            master     text,
            has_owner  int,
            PRIMARY KEY (file, key))
    """)
    database.query("""
        create table if not exists options (
            name text primary key,
            value text)
    """)

  def option(self, name):
    value = database.query('select value from options where name=? limit 1', (name, )).fetchone()
    if value is not None:
      return value['value']
    return None

  def setOption(self, name, value):
    v = self.option(name)
    if v is not None:
      database.query('update options set value=? where name=?', (value, name))
    else:
      database.query('insert into options (name, value) values (?,?)', (name, value))

  def calcTranslationHash(self):
    hasher = CHasher(self._translation_file, '')
    for key in datasource[self._translation_file].keys():
      hasher.append(key)
      hasher.append(datasource[self._translation_file].get_src_language(key))
    return hasher.hash()

  def checkTranslationHash(self):
    option_name = f'{self._translation_file}_hash'
    rprint(f'[magenta3]Updating {self._translation_file} hash[/magenta3]')
    calculated_hash = self.calcTranslationHash()
    stored_hash = self.option(option_name)
    rprint(f'[dark_orange3]{self._translation_file} hash: {calculated_hash}; Stored hash: {stored_hash}[/dark_orange3]')
    if stored_hash != calculated_hash:
      rprint(f'[red1]Hashes not equal for {self._translation_file}: updated translation file (?). Cleanup some metadata... [/red1]')
      self._cleanupMetadata()
      self.setOption(option_name, calculated_hash)

  def _cleanupMetadata(self):
    database.query(f'delete from metadata where file=?', (self._translation_file, ))

  def _totalStrings(self, source):
    if source not in self._total_strings:
      self._total_strings[source] = datasource[source].count()
    return self._total_strings[source]

  def keyIsTranslated(self, key):
    cursor = database.query('select 1 from translation where file=? and key=? limit 1', (self._translation_file, key))
    return cursor.fetchone() is not None

  def _translationHash(self, key, query_context):
    hasher = CHasher(self._translation_file, key)
    hasher.append(query_context)
    return hasher.hash()

  def setTranslated(self, key, original_text, translated_text, query_context):
    context_hash = self._translationHash(key, query_context)
    if self.keyIsTranslated(key):
      database.query('update translation set original_text=?, translated_text=?, context_hash=? where file=? and key=?',
                      (original_text, translated_text, context_hash, self._translation_file, key) )
    else:
      database.query('insert into translation (file, key, original_text, translated_text, context_hash) values (?,?,?,?,?)',
                      (self._translation_file, key, original_text, translated_text, context_hash) )

  def storedTranslation(self, key, original_text, query_context):
    context_hash = self._translationHash(key, query_context)
    ot = database.query('select translated_text from translation where file=? and key=? and original_text=? and context_hash=? limit 1',
                                          (self._translation_file, key, original_text, context_hash)).fetchone()
    return ot['translated_text'] if ot is not None else None

  # duplicates and owners
  def _isSlaveExists(self, key):
    cursor = database.query('select 1 from metadata where file=? and key=? limit 1', (self._translation_file, key, ))
    return cursor.fetchone() is not None

  def appendDuplicateKey(self, master_key, key):
    if self._isSlaveExists(key):
      database.query('update metadata set master=? where file=? and key=?', (master_key, self._translation_file, key) )
    else:
      database.query('insert into metadata (file, key, master) values (?,?,?)', (self._translation_file, key, master_key) )

  def isDuplicateKey(self, key):
    cursor = database.query('select 1 from metadata where file=? and key=? and master is not null limit 1', (self._translation_file, key))
    return cursor.fetchone() is not None

  # def ownedKeys(self):
  #   cursor = database.query('select key from metadata where file=? and has_owner=1', (self._translation_file, ))
  #   return [row[0] for row in cursor.fetchall()]

  def appendOwnedKey(self, key):
    if self._isSlaveExists(key):
      database.query('update metadata set has_owner=1 where file=? and key=?', (self._translation_file, key) )
    else:
      database.query('insert into metadata (file, key, has_owner) values (?,?,1)', (self._translation_file, key) )

  def isOwnedKey(self, key):
    cursor = database.query('select 1 from metadata where file=? and key=? and has_owner == 1 limit 1', (self._translation_file, key))
    return cursor.fetchone() is not None

  def getStringsCounts(self):
    processed = database.query('SELECT count(*) as count FROM translation where file=?', (self._translation_file, )).fetchone()
    duplicates = database.query('SELECT count(*) as count FROM metadata where file=? and master is not null', (self._translation_file, )).fetchone()
    return  {
              'total': self._totalStrings(self._translation_file),
              'translated': processed['count'] + duplicates['count']
            }

  def showTranslateState(self):

    translated = database.query("""
                                select
                                    file,
                                    (select count(*) from translation t where t.file = f.file) as translation_count,
                                    (select count(*) from metadata s where s.file = f.file and s.master is not null) as duplicates
                                from (
                                    select file from translation
                                    union
                                    select file from metadata
                                ) as f
                                order by file;
                                """)

    table = Table(title="Translate process", expand=True)
    table.add_column("Source"           , style="yellow"     , no_wrap=False)
    table.add_column("Translated"       , style="magenta"    , no_wrap=False)
    table.add_column("with Duplicates"  , style="grey50"     , no_wrap=False)
    table.add_column("Total strings"    , style="dark_violet", no_wrap=False)
    totals = {'translated': 0, 'duplicates': 0, 'total': 0}
    for row in translated:
      table.add_row(row['file'], str(row['translation_count'] + row['duplicates']), str(row['duplicates']), str(self._totalStrings(row['file'])))
      totals['translated'] += row['translation_count'] + row['duplicates']
      totals['duplicates'] += row['duplicates']
      totals['total'] += self._totalStrings(row['file'])
    table.add_row('Total', str(totals['translated']), str(totals['duplicates']), str(totals['total']))
    Console().print(table)
