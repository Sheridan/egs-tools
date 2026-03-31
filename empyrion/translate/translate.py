import time
import json
import pprint
import re
import inspect
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.markup import escape
from empyrion.ollama import COllama, СOllamaError
from empyrion.helpers.templating import CTemplating
from empyrion.options import options
from empyrion.helpers.tagcomparator import TagComparator
from empyrion.translate.lexicon.glossary import CGlossary
from empyrion.translate.lexicon.characters import CCharacters
from empyrion.translate.lexicon.examples import CExamples
from empyrion.helpers.hasher import CHasher
from empyrion.datasource.datasource import datasource
from empyrion.state.state import state
from empyrion.helpers.strings import text_for_translate, replace_literals_newlines_by_newlines, replace_newlines_by_literals_newlines, similarity_sequence

class CTranslate:
  def __init__(self, translation_file):
    self._translation_file = translation_file
    self._translation = datasource[self._translation_file]
    self._llm = COllama()
    self._templating = CTemplating()
    self._sleep_on_error = 8
    self._src_language=options.get("translation.src_language", "English")
    self._dst_language=options.get("translation.dst_language", "Russian")
    self._wrongs_to_switch_to_smart = options.get("ollama.models.wrongs_to_switch_to_smart", 4)
    self._glossary = CGlossary()
    self._characters = CCharacters()
    self._examples = CExamples()
    self._wrong_translate = []
    self._wrongs_count = 0
    self._counts = {
      'total': 0,
      'translated': 0
    }
    self._save_event_counter = 0
    self._save_event_max = options.get("translation.save_every_nth_query", 10)

  def _checkNeedToSave(self):
    self._save_event_counter += 1
    if self._save_event_counter >= self._save_event_max:
      self._translation.save()
      state.save()
      self._save_event_counter = 0

  def _setTotalStrings(self, total):
    self._counts['total'] = total

  def _incrementTranslated(self):
    self._counts['translated'] += 1

  def _translationProgress(self):
    return f"|[yellow]{self._counts['translated'] + 1} of {self._counts['total']}[/yellow]|"

  def _queryLog(self, query, current):
    if options.get("debug", False):
      table = Table(show_lines=True, expand=True)
      table.add_column("---"  , style="magenta", no_wrap=False, highlight=False)
      table.add_column("Debug", style="yellow" , no_wrap=False, highlight=False)
      table.add_row("Query"   , escape(query)  )
      table.add_row("Response", escape(current))
      Console().print(table)

  def translateLog(self, text, previous, current):
    table = Table(title='Texts', caption=f'Similarity between Previous and Current: {similarity_sequence(previous, current):.2f}%', expand=True)
    table.add_column("Source"    , style="yellow", no_wrap=False, highlight=False)
    table.add_column("Previous"  , style="bold"  , no_wrap=False, highlight=False)
    table.add_column("Current"   , style="green" , no_wrap=False, highlight=False)
    table.add_row(escape(text), escape(previous), escape(current))
    Console().print(table)

  def _translateShortLog(self, text, current):
    table = Table(expand=True)
    table.add_column("Source" ,  style="yellow", no_wrap=False, highlight=False)
    table.add_column("Current",  style="green" , no_wrap=False, highlight=False)
    table.add_row(escape(text), escape(current))
    Console().print(table)

  def _fileLog(self, key, src_language_text, dst_language_text):
    log_filename = f'trash/{self._translation_file}.translate.log'
    with open(log_filename, 'a', encoding='utf-8') as log_file:
      lines = [
        f'----==[ {key} ]==----',
        replace_literals_newlines_by_newlines(src_language_text),
        '------- vvvv -------',
        replace_literals_newlines_by_newlines(dst_language_text),
        ':'*80
      ]
      log_file.write("\n".join(lines) + '\n')

  def _resetWrongs(self):
    self._wrongs_count = 0
    del self._wrong_translate[:]

  def _countEnglishEetters(self, text):
    return sum(1 for c in text if 'a' <= c <= 'z' or 'A' <= c <= 'Z')

  def _prepareText(self, text):
    return replace_literals_newlines_by_newlines(text).strip()

  def _fixResponse(self, text, response):
    for char in ['\n', '.']:
      if text[-1] != char and response[-1] == char:
        response = response[:-1]
    for char in ['>', ']']:
      if text[-1] == char and response[-1] != char:
        response += char
    return replace_newlines_by_literals_newlines(response).strip()

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

  def _findAndTranslateSame(self, original_key, original_text, translated_text):
    for key in self._translation.keys():
      if key != original_key:
        src_text = self._translation.get_src_language(key)
        if src_text.strip() == original_text.strip():
          self._translation.set_dst_language(key, translated_text)
          state.appendDuplicateKey(self._translation_file, key)
          self._checkNeedToSave()
          rprint(f'[magenta]Same text found and translate in [bold]{key}[/bold][/magenta]')

  def _prepareQueryContext(self, text, object_context):
    return {
      'object_context': object_context,
      'glossary'      : self._glossary.filterByText(text),
      'characters'    : self._characters.filterByText(text),
      'examples'      : self._examples.filterByText(text),
    }

  def _translateOne(self, what, key, object_context):
    if not self._translation.exists(key):
      rprint(f'{self._translationProgress()} [red]{what.title()} [bold]{key} not exists in translation file![/bold][/red]')
      self._incrementTranslated()
      return

    original_text = self._translation.get_src_language(key)
    text = text_for_translate(original_text)
    query_context = self._prepareQueryContext(text, object_context)
    hasher = CHasher(self._translation_file, key)
    hasher.append(text)
    hasher.append(query_context)

    if state.isTranslated(hasher):
      rprint(f'{self._translationProgress()} [green]{what.title()} [bold]{key}[/bold] already translated[/green]')
      self._incrementTranslated()
      return

    if state.isDuplicateKey(self._translation_file, key):
      rprint(f'{self._translationProgress()} [green]{what.title()} [bold]{key}[/bold] value is [magenta]duplicate[/magenta] of another {what}[/green]')
      state.appendTranslateState(hasher)
      self._incrementTranslated()
      return

    rprint(f'{self._translationProgress()} [green]Translating {what} [bold]{key}[/bold][/green]')
    translated_text = self._translate(query_context, text)
    state.appendTranslateState(hasher)
    self.translateLog(text, self._translation.get_dst_language(key), translated_text)
    self._fileLog(key, text, translated_text)
    self._translation.set_dst_language(key, translated_text)
    self._incrementTranslated()
    self._checkNeedToSave()
    self._findAndTranslateSame(key, original_text, translated_text)
    state.showKnownKeysTranslateState()


  def _translate(self, query_context, text):
    result = None

    while result is None:
      try:
        prepared_text = self._prepareText(text)
        query = self._templating.loadTemplate('prompts', 'system.prompt').render(
            context=query_context['object_context'],
            src_language=self._src_language,
            dst_language=self._dst_language,
            glossary=query_context['glossary'],
            characters=query_context['characters'],
            examples=query_context['examples'],
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
      except СOllamaError as e:
        rprint(f"[red]LLM query failed: {escape(str(e))}. Retrying in {self._sleep_on_error} seconds...[/red]")
        time.sleep(self._sleep_on_error)
    return self._fixResponse(text, result)
