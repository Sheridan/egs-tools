import time
import json
import pprint
import re
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.markup import escape
from empyrion.ollama import COllama
from empyrion.helpers.templating import CTemplating
from empyrion.helpers.state import StateStorage
from empyrion.options import options
from empyrion.helpers.tagcomparator import TagComparator
from empyrion.translation import translation

class CTranslate:
  def __init__(self, state_name, translation_file):
    self._translation = translation[translation_file]
    self._llm = COllama()
    self._templating = CTemplating()
    self._state = StateStorage(f"trash/translate_{state_name}.state")
    self._sleep_on_error = 8
    self._src_language=options.get("translation.src_language", "English")
    self._dst_language=options.get("translation.dst_language", "Russian")
    self._wrongs_to_switch_to_smart = options.get("ollama.models.wrongs_to_switch_to_smart", 4)
    self._glossary = self._loadGlossary()
    self._wrong_translate = []
    self._wrongs_count = 0
    self._counts = {
      'total': 0,
      'translated': 0
    }

  def _setTotalStrings(self, total):
    self._counts['total'] = total

  def _incrementTranslated(self):
    self._counts['translated'] += 1

  def _translationProgress(self):
    return f"|[yellow]{self._counts['translated'] + 1} of {self._counts['total']}[/yellow]|"

  def _loadGlossary(self):
    with open(f'glossary/{self._dst_language}.json', 'r', encoding='utf-8') as f:
        return json.load(f)

  def _queryLog(self, query, current):
    if options.get("debug", False):
      table = Table(show_lines=True, expand=True)
      table.add_column("---"  , style="magenta", no_wrap=False, highlight=False)
      table.add_column("Debug", style="yellow" , no_wrap=False, highlight=False)
      table.add_row("Query"   , escape(query)  )
      table.add_row("Response", escape(current))
      Console().print(table)

  def translateLog(self, text, previous, current):
    table = Table(expand=True)
    table.add_column("Source"  , style="yellow", no_wrap=False, highlight=False)
    table.add_column("Previous", style="bold"  , no_wrap=False, highlight=False)
    table.add_column("Current" , style="green" , no_wrap=False, highlight=False)
    table.add_row(escape(text), escape(previous), escape(current))
    Console().print(table)

  def _translateShortLog(self, text, current):
    table = Table(expand=True)
    table.add_column("Source" ,  style="yellow", no_wrap=False, highlight=False)
    table.add_column("Current",  style="green" , no_wrap=False, highlight=False)
    table.add_row(escape(text), escape(current))
    Console().print(table)

  def _resetWrongs(self):
    self._wrongs_count = 0
    del self._wrong_translate[:]

  def _countEnglishEetters(self, text):
    return sum(1 for c in text if 'a' <= c <= 'z' or 'A' <= c <= 'Z')

  def removeTags(self, text):
    # return text
    text = re.sub(r'\[.*?\]', '', text)
    text = re.sub(r'<.*?>', '', text)
    return text

  def addToState(self, key):
    self._state.set(key)

  def inState(self, key):
    return self._state.exists(key)

  def _prepareText(self, text):
    return text.replace('\\n', '\n').strip()

  def _fixResponse(self, text, response):
    for char in ['\n', '.']:
      if text[-1] != char and response[-1] == char:
        response = response[:-1]
    for char in ['>', ']']:
      if text[-1] == char and response[-1] != char:
        response += char
    return response.replace('\n', '\\n').strip()

  def _addToWrongs(self, result, reason):
    rprint(f'[bright_red]Wrong translate. {reason}[/bright_red]')
    self._wrongs_count += 1
    for item in self._wrong_translate:
      if item['text'] == result and item['reason'] == reason:
        return
    self._wrong_translate.append({
      'text': result,
      'reason': reason
    })

  def _checkResponse(self, text, result):
    text_is_plhldr_or_tag = text[0] in ['[', '{'] and text[-1] in [']', '}']
    if (self._countEnglishEetters(result) / 2) > len(result):
      self._addToWrongs(result, f'There is more than half of the untranslated text left. {self._countEnglishEetters(result) / 2} > {len(result)}')
      self._translateShortLog(text, result)
      return None
    if (len(text) * 4) < len(result):
      self._addToWrongs(result, f'Result length ({len(result)}) is much larger than the original ({len(text)})')
      self._translateShortLog(text, result)
      return None
    if not text_is_plhldr_or_tag and text == result:
      self._addToWrongs(result, f'Result unchanged')
      self._translateShortLog(text, result)
      return None
    if result.strip() == '':
      self._addToWrongs(result, 'Result empty')
      self._translateShortLog(text, result)
      return None
    if not text_is_plhldr_or_tag and not TagComparator(text).compare(result):
      self._addToWrongs(result, f'The tags are specified incorrectly')
      self._translateShortLog(text, result)
      return None
    return result

  def _filteredGlossary(self, text):
    filtered = {}
    l_text = text.lower()
    for group in self._glossary.keys():
      for key in self._glossary[group].keys():
        for key_word in key.lower().split():
          if key_word in l_text:
            filtered[key] = self._glossary[group][key]
    # pprint.pprint(filtered)
    return filtered

  def _findAndTranslateSame(self, src_language_text, dst_language_text):
    for key in self._translation.keys():
      if not self.inState(key):
        src_text = self._translation.get_src_language(key)
        if src_text.strip() == src_language_text.strip():
          self._translation.set_dst_language(key, dst_language_text)
          self.addToState(key)
          # self._incrementTranslated()
          rprint(f'[magenta]Same text found and translate in [bold]{key}[/bold][/magenta]')

  def _translateOne(self, what, key, context):
    # rprint(context)
    if self.inState(key):
      rprint(f'{self._translationProgress()} [green]{what.title()} [bold]{key}[/bold] already translated[/green]')
      self._incrementTranslated()
      return
    if self._translation.exists(key):
      rprint(f'{self._translationProgress()} [green]Translating {what} [bold]{key}[/bold][/green]')
      text = self._translation.get_src_language(key)
      result = self._translate(context, text)
      self.addToState(key)
      self.translateLog(text, self._translation.get_dst_language(key), result)
      self._translation.set_dst_language(key, result)
      self._incrementTranslated()
      self._findAndTranslateSame(text, result)

  def _translate(self, context, text):
    result = None
    glossary = self._filteredGlossary(text)
    while result is None:
      try:
        prepared_text = self._prepareText(text)
        query = self._templating.loadTemplate('prompts', 'system.prompt').render(
            context=context,
            src_language=self._src_language,
            dst_language=self._dst_language,
            glossary=glossary,
            text=prepared_text,
            wrongs=self._wrong_translate
          )
        query_result = self._llm.query(query)
        self._queryLog(query, query_result)
        result = self._checkResponse(prepared_text, query_result)
        if self._wrongs_count >= self._wrongs_to_switch_to_smart:
          self._llm.switchToSmartModel()
        if result is not None:
          self._resetWrongs()
          self._llm.switchToMainModel()
      except Exception as e:
        rprint(f"[red]LLM query failed: {escape(str(e))}. Retrying in {self._sleep_on_error} seconds...[/red]")
        time.sleep(self._sleep_on_error)
    return self._fixResponse(text, result)
