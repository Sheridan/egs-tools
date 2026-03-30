
import os
import json
import hashlib
import statistics

from rich.console import Console
from rich.table import Table
from rich.markup import escape
from rich import print as rprint

from empyrion.state.history import CHistory

class CState:
  def __init__(self):
    self._filename = "trash/state.json"
    self._data = {}
    self._load()

  def _load(self):
    if not os.path.exists(self._filename):
      return
    try:
      with open(self._filename, 'r', encoding='utf-8') as f:
        content = f.read().strip()
        if not content:
          return
        self._data = json.loads(content)
    except (json.JSONDecodeError, IOError):
      self._data = {}

  def _createHash(self, text):
    encoded_text = text.encode('utf-8')
    hash_object = hashlib.md5(encoded_text)
    md5_hash = hash_object.hexdigest()
    return md5_hash

  def save(self):
    rprint(f"[blue]Saving {self._filename}[/blue]...")
    dir_name = os.path.dirname(self._filename)
    if dir_name:
      os.makedirs(dir_name, exist_ok=True)

    with open(self._filename, 'w', encoding='utf-8') as f:
      json.dump(self._data, f, ensure_ascii=False, indent=2)

  def _ensureSectionExists(self, tool, section):
    if tool not in self._data:
      self._data[tool] = {}
    if section not in self._data[tool]:
      self._data[tool][section] = {}

  def _toolExists(self, tool):
    return tool in self._data

  def _sectionExists(self, tool, section):
    if not self._toolExists(tool):
      return False
    return section in self._data[tool]

  # list
  def _add(self, tool, section, name, value):
    self._ensureSectionExists(tool, section)
    if name not in self._data[tool][section]:
      self._data[tool][section][name] = []
    self._data[tool][section][name].append(value)

  # dict
  def _set(self, tool, section, name, value):
    self._ensureSectionExists(tool, section)
    if name not in self._data[tool][section]:
      self._data[tool][section][name] = {}
    self._data[tool][section][name] = value

  def _tool(self, tool):
    if self._toolExists(tool):
      return self._data[tool]
    return None

  def _section(self, tool, section):
    if self._sectionExists(tool, section):
      return self._data[tool][section]
    return None

  def appendTranslateState(self, translate_src, key, src_lng_text):
    # translate_src: pda, localization, dialogues
    self._set('translation', translate_src, key, {
      'hash': self._createHash(src_lng_text)
    })

  def isTranslated(self, translate_src, key, src_lng_text):
    section = self._section('translation', translate_src)
    if section is None:
      return False
    if key not in section.keys():
      return False
    return section[key]['hash'] == self._createHash(src_lng_text)

  def appendLLMQueryState(self, llm_model, elapsed_time, in_tokens, out_tokens):
    self._add('llm', llm_model, 'query_elapsed_time', elapsed_time)
    self._add('llm', llm_model, 'query_tokens_in'   , in_tokens)
    self._add('llm', llm_model, 'query_tokens_out'  , out_tokens)

  def showTranslateState(self):
    translation = self._tool('translation')
    if translation is None:
      return
    total = 0
    table = Table(title="Keys translated", expand=True)
    table.add_column("Source"    , style="yellow" , no_wrap=False)
    table.add_column("Translated", style="magenta", no_wrap=False)
    for section_name in translation:
      s_len = len(translation[section_name])
      table.add_row(section_name, str(s_len))
      total += s_len
    table.add_row('Total', str(total))
    Console().print(table)

  def _formatSeconds(self, seconds: float) -> str:
    total_seconds = int(round(seconds))
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    secs = total_seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"

  def showLLMState(self):
    llm = self._tool('llm')
    if llm is None:
      return
    history = { }
    total = { 'elapsed_time': CHistory(),
              'tokens_in':    CHistory(),
              'tokens_out':   CHistory() }
    for model in llm.keys():
      if 'query_elapsed_time' in llm[model] and 'query_tokens_in' in llm[model] and 'query_tokens_out' in llm[model]:
        if model not in history:
          history[model] = { 'elapsed_time': CHistory(),
                             'tokens_in':    CHistory(),
                             'tokens_out':   CHistory() }
        history[model]['elapsed_time'].append(llm[model]['query_elapsed_time'])
        history[model]['tokens_in']   .append(llm[model]['query_tokens_in'])
        history[model]['tokens_out']  .append(llm[model]['query_tokens_out'])
        total['elapsed_time'].append(llm[model]['query_elapsed_time'])
        total['tokens_in']   .append(llm[model]['query_tokens_in'])
        total['tokens_out']  .append(llm[model]['query_tokens_out'])


    table = Table(title="LLM statistics", expand=True)
    table.add_column("Model"           , style="cyan")
    table.add_column("Queries"         , style="bright_magenta")
    table.add_column("Query\nmean"      , style="dark_cyan")
    table.add_column("Query\nmedian"    , style="light_sea_green")
    table.add_column("Query\nmax"       , style="deep_sky_blue2")
    table.add_column("Query\nmin"       , style="deep_sky_blue1")
    table.add_column("Query\ntotal"     , style="aquamarine3")
    table.add_column("Tokens\nin"       , style="yellow2")
    table.add_column("Tokens\nin\nmin"   , style="dark_sea_green1")
    table.add_column("Tokens\nin\nmean"  , style="honeydew2")
    table.add_column("Tokens\nin\nmax"   , style="light_cyan1")
    table.add_column("Tokens\nout"      , style="dark_olive_green1")
    for model in history.keys():
      table.add_row(escape(model),
                    str(history[model]['elapsed_time'].count()),
                    escape(self._formatSeconds(history[model]['elapsed_time'].mean())),
                    escape(self._formatSeconds(history[model]['elapsed_time'].median())),
                    escape(self._formatSeconds(history[model]['elapsed_time'].max())),
                    escape(self._formatSeconds(history[model]['elapsed_time'].min())),
                    escape(self._formatSeconds(history[model]['elapsed_time'].sum())),
                    str(int(history[model]['tokens_in'   ].sum())),
                    str(int(history[model]['tokens_in'   ].min())),
                    str(int(history[model]['tokens_in'   ].mean())),
                    str(int(history[model]['tokens_in'   ].max())),
                    str(int(history[model]['tokens_out'  ].sum())))
    table.add_row('Total',
                    str(total['elapsed_time'].count()),
                    escape(self._formatSeconds(total['elapsed_time'].mean())),
                    escape(self._formatSeconds(total['elapsed_time'].median())),
                    escape(self._formatSeconds(total['elapsed_time'].max())),
                    escape(self._formatSeconds(total['elapsed_time'].min())),
                    escape(self._formatSeconds(total['elapsed_time'].sum())),
                    str(int(total['tokens_in'].sum())),
                    str(int(total['tokens_in'].min())),
                    str(int(total['tokens_in'].mean())),
                    str(int(total['tokens_in'].max())),
                    str(int(total['tokens_out'].sum())))
    Console().print(table)

state = CState()
