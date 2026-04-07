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
from empyrion.translate.lexicon.glossary import glossary
from empyrion.translate.lexicon.characters import characters
from empyrion.translate.lexicon.examples import examples
from empyrion.helpers.hasher import CHasher
from empyrion.datasource.datasource import datasource
from empyrion.state.state import state
from empyrion.state.translationstorage import CTranslationStorage
from empyrion.statistics.statistics import statistics
from empyrion.helpers.strings import text_for_translate, replace_literals_newlines_by_newlines, replace_newlines_by_literals_newlines, similarity_sequence, rich_colorize_hex, no_letters
from empyrion.helpers.filesystem import append_to_file
from empyrion.markup.tagsprocessor import tags_processor
from empyrion.markup.placeholdersprocessor import placeholders_processor
from empyrion.markup.atanchorsprocessor import atanchors_processor
from empyrion.translate.translationchecker import CTranslationChecker
import empyrion.helpers.color as clr

class CTranslate:
  def __init__(self, translation_file):
    self._translation_file = translation_file
    self._translation = datasource[self._translation_file]
    state.setStringsTotal(self._translation_file, self._translation.count())
    self._llm = COllama()
    self._templating = CTemplating()
    self._translation_storage = CTranslationStorage(self._translation_file)
    self._sleep_on_error = 8
    self._src_language=options.get("translation.src_language", "English")
    self._dst_language=options.get("translation.dst_language", "Russian")
    self._max_query_tryes=options.get("ollama.max_tryes", 16)
    self._wrongs_to_switch_to_smart = options.get("ollama.models.wrongs_to_switch_to_smart", 4)
    self._counts = {
      'total': 0,
      'translated': 0
    }
    self._untranslable = options.get("translation.untranslable_strings", [])
    self._save_event_counter = 0
    self._save_event_max = options.get("translation.save_every_nth_query", 10)

  def saveAll(self):
    self._translation.save()
    state.save()
    statistics.save()
    self._translation_storage.save()

  def _checkNeedToSave(self):
    self._save_event_counter += 1
    if self._save_event_counter >= self._save_event_max:
      self.saveAll()
      self._save_event_counter = 0
      state.showKnownKeysTranslateState()
      statistics.showLLM()

  def _setTotalObjects(self, total):
    self._counts['total'] = total

  def _incrementTranslatedObjects(self):
    self._counts['translated'] += 1

  def _translationProgress(self, caption, key):
    return rprint(f"|[yellow]{self._counts['translated'] + 1} of {self._counts['total']}[/yellow]| Processing {clr.objCaption(caption)} with key {clr.key(key)}")

  def translateLog(self, key, text, previous, current):
    table = Table(title=f'Translation {self._translation_file} {clr.key(key)}', caption=f'Similarity between Previous and Current: {similarity_sequence(previous, current):.2f}%', expand=True)
    table.add_column(f'Source ({len(text)} symbols)'      , style='yellow', no_wrap=False, highlight=False)
    table.add_column(f'Previous ({len(previous)} symbols)', style='bold'  , no_wrap=False, highlight=False)
    table.add_column(f'Current ({len(current)} symbols)'  , style='green' , no_wrap=False, highlight=False)
    table.add_row(rich_colorize_hex(escape(replace_literals_newlines_by_newlines(text))),
                  rich_colorize_hex(escape(replace_literals_newlines_by_newlines(previous))),
                  rich_colorize_hex(escape(replace_literals_newlines_by_newlines(current))))
    Console().print(table)
    self._fileLog(table)

  def _fileLog(self, table):
    log_filename = f'trash/.log'
    console = Console(no_color=True, force_terminal=False)
    with console.capture() as capture:
      console.print(table)
    table_str = capture.get()
    append_to_file(f'{self._translation_file}.translate', table_str)

  def _countEnglishLetters(self, text):
    return sum(1 for c in text if 'a' <= c <= 'z' or 'A' <= c <= 'Z')

  def _fixResponse(self, text, response):
    for char in ['\n', '.']:
      if text[-1] != char and response[-1] == char:
        response = response[:-1]
    for char in ['"', '`', "'"]:
      while True:
        if text[0] != char and response[0] == char and text[-1] != char and response[-1] == char:
          response = response[1:-1]
        else:
          break
    return replace_newlines_by_literals_newlines(response).strip()

  def _textIsPlaceholderOrTag(self, s):
    return re.fullmatch(r'[\[\{][a-zA-Z0-9]+[\]\}]', s)

  def _findAndTranslateSame(self, original_key, original_text, translated_text):
    for key in self._translation.keys():
      if key != original_key and not state.isDuplicateKey(self._translation_file, key): # and not state.keyIsTranslated(self._translation_file, key):
        src_text = self._translation.get_src_language(key)
        if src_text.strip() == original_text.strip():
          self._translation.set_dst_language(key, translated_text)
          state.appendDuplicateKey(self._translation_file, key)
          state.incrementTranslatedStrings(self._translation_file)
          self._checkNeedToSave()
          rprint(f'[dark_violet]Same text found and translate in {clr.key(key)}[/dark_violet]')

  def _isUntranslable(self, text):
    if no_letters(tags_processor.removeTags(text).strip()):
      return True
    for part in self._untranslable:
      if part in text:
        return True
    return False

  def _reTranslateNeeded(self, key, original_text):
    translation_checker = CTranslationChecker(original_text, self._translation.get_dst_language(key))
    if not translation_checker.check():
      translation_checker.show()
      return True, translation_checker.errorsAsContext()
    return False, {}

  def _prepareQueryContext(self, text, object_context):
    # print(list(set(atanchors_processor.extract(text))))
    return {
      'object_context': object_context,
      'glossary'      : glossary.filter(text),
      'characters'    : characters.filter(text, object_context),
      'examples'      : examples.filter(text),
      'placeholders'  : list(set(placeholders_processor.extract(text))),
      'anchors'       : list(set(atanchors_processor.extract(text))),
      'tags'          : tags_processor.tagsList(text)
    }

  def _translateOne(self, what, key, object_context):
    if not self._translation.exists(key):
      rprint(f'[red]{what.title()} {clr.key(key)} not exists in translation file![/red]')
      return
    original_text = self._translation.get_src_language(key)
    text = text_for_translate(original_text)
    query_context = self._prepareQueryContext(text, object_context)
    hasher = CHasher(self._translation_file, key)
    hasher.append(text)
    hasher.append(query_context)
    state.appendOwnedKey(self._translation_file, key)
    self._translate(key, what, original_text, text, query_context, hasher)


  def _translate(self, key, what, original_text, text, query_context, hasher):

    if len(original_text.strip()) == 0:
      rprint(f'[green]{what.title()} {clr.key(key)} text of {what} is [magenta]empty[/magenta].[/green] [grey62]We are not doing anything[/grey62]')
      return

    if self._isUntranslable(original_text):
      rprint(f'[green]{what} {clr.key(key)}[/green] [yellow]no need translation[/yellow] [grey62]We are not doing anything[/grey62]')
      return

    if state.isDuplicateKey(self._translation_file, key):
      rprint(f'[green]{what.title()} {clr.key(key)} value is [magenta]duplicate[/magenta] of another {what}.[/green] [grey62]We are not doing anything[/grey62]')
      return

    retranslation_needed, translation_errors = self._reTranslateNeeded(key, original_text)
    if state.isTranslated(hasher) and not retranslation_needed:
      rprint(f'[green]{what.title()} {clr.key(key)} already translated[/green]')
      return

    if self._translation_storage.exists(key, original_text, query_context) and self._translation.get_dst_language(key) != self._translation_storage.get(key):
      rprint(f'[green]{what.title()} {clr.key(key)} taked from translation storage[/green]')
      self._translation.set_dst_language(key, self._translation_storage.get(key))
      state.incrementTranslatedStrings(self._translation_file)
      return

    counts = state.getStringsCounts(self._translation_file)
    rprint(f'[green]|{counts['processed']} of {counts['total']}| Translating {what} {clr.key(key)}[/green]')
    translated_text = self._query(query_context, text, translation_errors)
    self.translateLog(key, text, self._translation.get_dst_language(key), translated_text)
    self._translation.set_dst_language(key, translated_text)
    if not state.keyIsTranslated(self._translation_file, key):
      state.incrementTranslatedStrings(self._translation_file)
    state.appendTranslateState(hasher)
    self._translation_storage.set(key, original_text, translated_text, query_context)
    self._findAndTranslateSame(key, original_text, translated_text)
    self._checkNeedToSave()

  def _query(self, query_context, text, translation_errors = {}):
    queries_count = -1
    tryes = -1
    self._llm.switchToMainModel()
    while True:
      try:
        queries_count += 1
        tryes += 1
        if queries_count >= self._wrongs_to_switch_to_smart:
          self._llm.switchToSmartModel()
        prepared_text = replace_literals_newlines_by_newlines(text).strip()
        system_prompt = self._templating.loadTemplate('prompts', 'system.prompt').render(
            context      = query_context['object_context'],
            src_language = self._src_language,
            dst_language = self._dst_language,
            glossary     = query_context['glossary'],
            characters   = query_context['characters'],
            examples     = query_context['examples'],
            tags         = query_context['tags'],
            placeholders = query_context['placeholders'],
            anchors      = query_context['anchors']
          )
        user_prompt = self._templating.loadTemplate('prompts', 'user.prompt').render(
            src_language = self._src_language,
            dst_language = self._dst_language,
            errors       = translation_errors,
            text         = prepared_text
          )
        query_result = self._llm.query(system_prompt, user_prompt)
        translation_checker = CTranslationChecker(prepared_text, query_result)
        if translation_checker.check() or tryes >= self._max_query_tryes:
          return self._fixResponse(text, query_result)
        translation_checker.show()
        translation_errors = translation_checker.errorsAsContext()
      except СOllamaError as e:
        rprint(f"[red]LLM query failed: {escape(str(e))}. Retrying in {self._sleep_on_error} seconds...[/red]")
        time.sleep(self._sleep_on_error)

  def _translateTails(self):
    rprint(f'[yellow1]Translating orphan strings[/yellow1]')
    for key in self._translation.keys():
      if not state.isOwnedKey(self._translation_file, key):
        original_text = self._translation.get_src_language(key)
        text = text_for_translate(original_text)
        query_context = self._prepareQueryContext(text, {})
        hasher = CHasher(self._translation_file, key)
        hasher.append(text)
        hasher.append(query_context)
        self._translate(key, 'orphan string', original_text, text, query_context, hasher)
