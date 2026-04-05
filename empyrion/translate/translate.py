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
from empyrion.translate.lexicon.glossary import CGlossary
from empyrion.translate.lexicon.characters import CCharacters
from empyrion.translate.lexicon.examples import CExamples
from empyrion.helpers.hasher import CHasher
from empyrion.datasource.datasource import datasource
from empyrion.state.state import state
from empyrion.statistics.statistics import statistics
from empyrion.helpers.strings import text_for_translate, replace_literals_newlines_by_newlines, replace_newlines_by_literals_newlines, similarity_sequence, rich_colorize_hex, is_atanchor_in_text, no_letters
from empyrion.helpers.filesystem import append_to_file
from empyrion.helpers.tagsprocessor import tags_processor
import empyrion.helpers.color as clr

class CTranslate:
  def __init__(self, translation_file):
    self._translation_file = translation_file
    self._translation = datasource[self._translation_file]
    state.setStringsTotal(self._translation_file, self._translation.count())
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
    self._untranslable = options.get("translation.untranslable_strings", [])
    self._save_event_counter = 0
    self._save_event_max = options.get("translation.save_every_nth_query", 10)

  def _checkNeedToSave(self):
    self._save_event_counter += 1
    if self._save_event_counter >= self._save_event_max:
      self._translation.save()
      state.save()
      statistics.save()
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

  def _translateShortLog(self, text, current):
    table = Table(expand=True)
    table.add_column("Source" ,  style="yellow", no_wrap=False, highlight=False)
    table.add_column("Current",  style="green" , no_wrap=False, highlight=False)
    table.add_row(escape(text), escape(current))
    Console().print(table)

  def _fileLog(self, table):
    log_filename = f'trash/.log'
    console = Console(no_color=True)
    with console.capture() as capture:
      console.print(table)
    table_str = capture.get()
    append_to_file(f'{self._translation_file}.translate', table_str)

  def _resetWrongs(self):
    self._wrongs_count = 0
    del self._wrong_translate[:]

  def _countEnglishLetters(self, text):
    return sum(1 for c in text if 'a' <= c <= 'z' or 'A' <= c <= 'Z')

  def _fixResponse(self, text, response):
    for char in ['\n', '.']:
      if text[-1] != char and response[-1] == char:
        response = response[:-1]
    return replace_newlines_by_literals_newlines(response).strip()

  def _addToWrongs(self, result, reason):
    rprint(f'[bright_red]Wrong translate.[/bright_red] [red1]{reason}[/red1]')
    self._wrongs_count += 1
    for item in self._wrong_translate:
      if item['text'] == result and item['reason'] == reason:
        return
    self._wrong_translate.append({
      'text': result,
      'reason': reason
    })

  def _textIsPlaceholderOrTag(self, s):
    return re.fullmatch(r'[\[\{][a-zA-Z0-9]+[\]\}]', s)

  def _checkResponse(self, source, result, query_context):
    if result.strip() == '':
        self._addToWrongs(result, 'Result empty')
        self._translateShortLog(source, result)
        return None
    if len(source) > 1 and len(result) > 1:
      if len(query_context['tags']) > 0 and not self._textIsPlaceholderOrTag(source) and not tags_processor.compare(source, result):
        self._addToWrongs(result, 'The tags are specified incorrectly')
        self._translateShortLog(source, result)
        return None
      source_without_tags = tags_processor.removeTags(source)
      result_without_tags = tags_processor.removeTags(result)
      if len(source_without_tags) > 1 and len(result_without_tags) > 1 and re.fullmatch(r'[0-9-\.\s]+', result_without_tags):
        if self._countEnglishLetters(result_without_tags) >= len(result_without_tags) / 2 and not self._glossary.isGlossaryPhrase(result_without_tags):
          self._addToWrongs(result, f'After tags remove there is more than half of the untranslated text left. {self._countEnglishLetters(result_without_tags)} > {len(result_without_tags) / 2}')
          self._translateShortLog(source, result)
          return None
        if len(source_without_tags) >= 4 and (len(source_without_tags) * 4) < len(result_without_tags):
          self._addToWrongs(result, f'After tags remove result length ({len(result_without_tags)}) is much larger than the original ({len(source_without_tags)})')
          self._translateShortLog(source, result)
          return None
        if not self._textIsPlaceholderOrTag(source_without_tags) and source_without_tags == result_without_tags and not self._glossary.isGlossaryPhrase(result_without_tags):
          self._addToWrongs(result, 'After remove tags result unchanged')
          self._translateShortLog(source, result)
          return None
      if len(query_context['placeholders']) > 0:
        for placeholder in query_context['placeholders']:
          if placeholder not in result_without_tags:
            self._addToWrongs(result, f'Missing placeholder {placeholder}')
            self._translateShortLog(source, result)
            return None
        for placeholder in self._extractPlaceholders(result_without_tags):
          if placeholder not in query_context['placeholders']:
            self._addToWrongs(result, f'Extra placeholder {placeholder}')
            self._translateShortLog(source, result)
            return None
    return result

  def _findAndTranslateSame(self, original_key, original_text, translated_text):
    for key in self._translation.keys():
      if key != original_key and not state.isDuplicateKey(self._translation_file, key): # and not state.keyIsTranslated(self._translation_file, key):
        src_text = self._translation.get_src_language(key)
        if src_text.strip() == original_text.strip():
          self._translation.set_dst_language(key, translated_text)
          state.appendDuplicateKey(self._translation_file, key)
          self._checkNeedToSave()
          rprint(f'[dark_violet]Same text found and translate in {clr.key(key)}[/dark_violet]')

  def _isUntranslable(self, text):
    if no_letters(tags_processor.removeTags(text).strip()):
      return True
    for part in self._untranslable:
      if part in text:
        return True
    return False

  def _extractPlaceholders(self, text):
    result = []
    start = None
    depth = 0

    for i, ch in enumerate(text):
      if ch == '{':
        if depth == 0:
          start = i  # начало нового плейсхолдера
        depth += 1
      elif ch == '}':
        if depth > 0:
          depth -= 1
          if depth == 0 and start is not None:
            result.append(text[start:i+1])
            start = None
    return result

  def _prepareQueryContext(self, text, object_context):
    return {
      'object_context': object_context,
      'glossary'      : self._glossary.filter(text),
      'characters'    : self._characters.filter(text, object_context),
      'examples'      : self._examples.filter(text),
      'placeholders'  : self._extractPlaceholders(text),
      'tags'          : tags_processor.tagsList(text)
    }

  def _translateOne(self, what, key, parent, object_context):
    if not self._translation.exists(key):
      rprint(f'[red]{what.title()} {clr.key(key)} not exists in translation file![/red]')
      return
    original_text = self._translation.get_src_language(key)
    text = text_for_translate(original_text)
    query_context = self._prepareQueryContext(text, object_context)
    hasher = CHasher(self._translation_file, key, parent)
    hasher.append(text)
    hasher.append(query_context)
    state.appendOwnedKey(self._translation_file, key)
    self._translate(key, what, original_text, text, query_context, hasher)


  def _translate(self, key, what, original_text, text, query_context, hasher):
    # if key == 'dialogue_mGauO':
    #   print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1111')
    #   rprint(query_context)
    #   print('!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!1111')
    if len(original_text.strip()) == 0:
      rprint(f'[green]{what.title()} {clr.key(key)} text of {what} is [magenta]empty[/magenta].[/green] [grey62]Only store hash[/grey62]')
      state.appendTranslateState(hasher)
      state.incrementTranslatedStrings(self._translation_file)
      return
    if self._isUntranslable(original_text):
      rprint(f'[green]{what} {clr.key(key)}[/green] [yellow]no need translation[/yellow]')
      state.incrementTranslatedStrings(self._translation_file)
      return
    if state.isDuplicateKey(self._translation_file, key):
      rprint(f'[green]{what.title()} {clr.key(key)} value is [magenta]duplicate[/magenta] of another {what}.[/green] [grey62]Only store hash[/grey62]')
      state.appendTranslateState(hasher)
      state.incrementTranslatedStrings(self._translation_file)
      state.rmDuplicateKey(self._translation_file, key)
      return
    if state.isTranslated(hasher):
      rprint(f'[green]{what.title()} {clr.key(key)} already translated[/green]')
      return
    counts = state.getStringsCounts(self._translation_file)
    rprint(f'[green]|{counts['processed']} of {counts['total']}| Translating {what} {clr.key(key)}[/green]')
    translated_text = self._query(query_context, text)
    self.translateLog(key, text, self._translation.get_dst_language(key), translated_text)
    self._translation.set_dst_language(key, translated_text)
    if not state.keyIsTranslated(self._translation_file, key):
      state.incrementTranslatedStrings(self._translation_file)
    state.appendTranslateState(hasher)
    self._findAndTranslateSame(key, original_text, translated_text)
    self._checkNeedToSave()


  def _query(self, query_context, text):
    result = None
    while result is None:
      try:
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
            wrongs       = self._wrong_translate,
            exists       = {
              'atanchors'   : is_atanchor_in_text(prepared_text)
            }
          )
        user_prompt = self._templating.loadTemplate('prompts', 'user.prompt').render(
            src_language = self._src_language,
            dst_language = self._dst_language,
            text         = prepared_text
          )
        query_result = self._llm.query(system_prompt, user_prompt)
        result = self._checkResponse(prepared_text, query_result, query_context)
        if self._wrongs_count >= self._wrongs_to_switch_to_smart:
          self._llm.switchToSmartModel()
        if result is not None:
          self._resetWrongs()
          self._llm.switchToMainModel()
      except СOllamaError as e:
        rprint(f"[red]LLM query failed: {escape(str(e))}. Retrying in {self._sleep_on_error} seconds...[/red]")
        time.sleep(self._sleep_on_error)
    return self._fixResponse(text, result)

  def _translateTails(self):
    rprint(f'[yellow1]Translating orphan strings[/yellow1]')
    parent = 'wihout_parent'
    for key in self._translation.keys():
      if not state.isOwnedKey(self._translation_file, key):
        original_text = self._translation.get_src_language(key)
        text = text_for_translate(original_text)
        query_context = self._prepareQueryContext(text, {})
        hasher = CHasher(self._translation_file, key, parent)
        hasher.append(text)
        hasher.append(query_context)
        self._translate(key, 'orphan string', original_text, text, query_context, hasher)
