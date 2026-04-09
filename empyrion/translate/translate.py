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
from empyrion.datasource.datasource import datasource
from empyrion.database.stat import statistics
from empyrion.helpers.strings import text_for_translate, replace_literals_newlines_by_newlines, replace_newlines_by_literals_newlines, similarity_sequence, rich_colorize_hex, no_letters
from empyrion.helpers.filesystem import append_to_file
from empyrion.markup.tagsprocessor import tags_processor
from empyrion.markup.placeholdersprocessor import placeholders_processor
from empyrion.markup.atanchorsprocessor import atanchors_processor
from empyrion.translate.translationchecker import CTranslationChecker
from empyrion.database.state import CStateDB
import empyrion.helpers.color as clr

class CTranslate:
  def __init__(self, translation_file):
    self._translation_file = translation_file
    self._translation = datasource[self._translation_file]
    self._llm = COllama()
    self._templating = CTemplating()
    self._db = CStateDB(self._translation_file)
    self._sleep_on_error = 8
    self._src_language=options.get("translation.src_language", "English")
    self._dst_language=options.get("translation.dst_language", "Russian")
    self._max_query_tryes=options.get("ollama.max_tryes", 16)
    self._objects_counts = { 'total': 0, 'translated': 0 }
    self._save_event_counter = 0
    self._save_event_max = options.get("translation.save_every_nth_query", 10)

  def saveAll(self):
    self._translation.save()

  def _checkNeedToSave(self):
    self._save_event_counter += 1
    if self._save_event_counter >= self._save_event_max:
      self.saveAll()
      self._save_event_counter = 0
      statistics.show()
      self._db.showTranslateState()

  def _setTotalObjects(self, total):
    self._objects_counts['total'] = total

  def _incrementTranslatedObjects(self):
    self._objects_counts['translated'] += 1

  def _objectsProgress(self, caption, key):
    return rprint(f"|[yellow]{self._objects_counts['translated'] + 1} of {self._objects_counts['total']}[/yellow]| Processing {clr.objCaption(caption)} with key {clr.key(key)}")

  def _stringsProgress(self):
    counts = self._db.getStringsCounts()
    return f'[medium_purple1]|{counts['processed']} of {counts['total']}|[/medium_purple1]'

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
    return replace_newlines_by_literals_newlines(response).strip()

  def _textIsPlaceholderOrTag(self, s):
    return re.fullmatch(r'[\[\{][a-zA-Z0-9]+[\]\}]', s)

  def _findAndTranslateSame(self, original_key, original_text, translated_text):
    for key in self._translation.keys():
      if key != original_key and not self._db.isDuplicateKey(key) and not self._db.keyIsTranslated(key):
        src_text = self._translation.get_src_language(key)
        if src_text.strip() == original_text.strip():
          self._translation.set_dst_language(key, translated_text)
          self._db.appendDuplicateKey(original_key, key)
          self._checkNeedToSave()
          rprint(f'{self._stringsProgress()} [dark_violet]Same text found and translate in {clr.key(key)}[/dark_violet]')

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
    text_4_translate = text_for_translate(original_text)
    query_context = self._prepareQueryContext(text_4_translate, object_context)
    self._db.appendOwnedKey(key)
    self._translate(key, what, original_text, text_4_translate, query_context)


  def _translate(self, key, what, original_text, text_4_translate, query_context):
    if len(original_text.strip()) == 0:
      rprint(f'[green]{what.title()} {clr.key(key)} text of {what} is [magenta]empty[/magenta].[/green] [grey62]We are not doing anything[/grey62]')
      return

    if glossary._isUntranslable(original_text):
      rprint(f'[green]{what} {clr.key(key)}[/green] [yellow]no need translation[/yellow] [grey62]We are not doing anything[/grey62]')
      return

    if self._db.isDuplicateKey(key):
      rprint(f'[green]{what.title()} {clr.key(key)} value is [magenta]duplicate[/magenta] of another {what}.[/green] [grey62]We are not doing anything[/grey62]')
      return

    translation_errors = {}
    if self._db.keyIsTranslated(key):
      retranslation_needed, translation_errors = self._reTranslateNeeded(key, text_4_translate)
      stored_translation = self._db.storedTranslation(key, text_4_translate, query_context)
      if stored_translation is not None and not retranslation_needed:
        if stored_translation != self._translation.get_dst_language(key):
          rprint(f'{self._stringsProgress()} [green]{what.title()}[/green] {clr.key(key)} [deep_sky_blue1]taked from translation storage[/deep_sky_blue1]')
          self._translation.set_dst_language(key, stored_translation)
          self._checkNeedToSave()
          return
        rprint(f'[green]{what.title()} {clr.key(key)} already translated[/green]')
        return

    rprint(f'{self._stringsProgress()} [green]Translating {what} {clr.key(key)}[/green]')
    translated_text = self._query(query_context, text_4_translate, translation_errors)
    self.translateLog(key, text_4_translate, self._translation.get_dst_language(key), translated_text)
    self._translation.set_dst_language(key, translated_text)
    self._db.setTranslated(key, original_text, translated_text, query_context)
    self._findAndTranslateSame(key, original_text, translated_text)
    self._checkNeedToSave()

  def _query(self, query_context, text_4_translate, translation_errors = {}):
    tryes = -1
    self._llm.switchToTranslatorModel()
    while True:
      try:
        tryes += 1
        if len(translation_errors):
          self._llm.switchToReasonerModel()
        prepared_text = replace_literals_newlines_by_newlines(text_4_translate).strip()
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
        translation_checker = CTranslationChecker(text_4_translate, query_result)
        if translation_checker.check() or tryes >= self._max_query_tryes:
          return self._fixResponse(text_4_translate, query_result)
        translation_checker.show()
        translation_errors = translation_checker.errorsAsContext()
      except СOllamaError as e:
        rprint(f"[red]LLM query failed: {escape(str(e))}. Retrying in {self._sleep_on_error} seconds...[/red]")
        time.sleep(self._sleep_on_error)

  def _translateTails(self):
    rprint(f'[yellow1]Translating orphan strings[/yellow1]')
    for key in self._translation.keys():
      if not self._db.isOwnedKey(key):
        original_text = self._translation.get_src_language(key)
        text_4_translate = text_for_translate(original_text)
        query_context = self._prepareQueryContext(text_4_translate, {})
        self._translate(key, 'orphan string', original_text, text_4_translate, query_context)
