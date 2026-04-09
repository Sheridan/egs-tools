from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.markup import escape
import unicodedata

from empyrion.markup.tagsprocessor import tags_processor
from empyrion.markup.placeholdersprocessor import placeholders_processor
from empyrion.markup.atanchorsprocessor import atanchors_processor
from empyrion.translate.lexicon.glossary import glossary
from empyrion.helpers.strings import count_english_letters, count_other_letters, replace_literals_newlines_by_newlines, text_for_context, quoted_list

class CTranslationChecker:
  def __init__(self, original, translated):
    self._original   = replace_literals_newlines_by_newlines(original)
    self._translated = replace_literals_newlines_by_newlines(translated)
    self._cleaned_original   = self._clean(original)
    self._cleaned_translated = self._clean(translated)
    self._errors = []

  def _clean(self, text):
    return text_for_context(text).strip()

  def _answerIsEmpty(self):
    if self._translated.strip() == '':
      self._errors.append('Translation is empty. Provide a complete translation of the source text.')

  def _entityToolCall(self, tool):
    if tool.exists(self._original):
      rc, message = tool.compare(self._original, self._translated)
      if not rc:
        self._errors.append(message)

  def _tagsDifferent(self): self._entityToolCall(tags_processor)
  def _placeholdersDifferent(self): self._entityToolCall(placeholders_processor)
  def _anchorsDifferent(self): self._entityToolCall(atanchors_processor)

  # def _tooManyUntranslated(self):
  # similarity = similarity_sequence(self._cleaned_original, self._cleaned_translated)
  # if similarity > 50:
  #   self._errors.append(f'Over {100 - similarity:.2f}% of the visible text remains untranslated. Translate the remaining content completely.')

  def _tooManyUntranslated(self):
    english_letters = count_english_letters(self._cleaned_translated)
    other_letters = count_other_letters(self._cleaned_translated)
    all_letters = other_letters + english_letters
    if all_letters > 0:
      percent = (english_letters / all_letters) * 100
      if percent > 80:
        self._errors.append(f'Over {percent:.2f}% of the visible text remains untranslated. Translate the remaining content completely.')

  def _answerTooLong(self):
    if len(self._cleaned_original) >= 4 and (len(self._cleaned_original) * 4) < len(self._cleaned_translated):
      self._errors.append(f'Translation is significantly longer than the source ({len(self._cleaned_translated)} vs {len(self._cleaned_original)}). Condense the text to match the original length while preserving meaning.')

  def _fullyUntranslated(self):
    if self._cleaned_original == self._cleaned_translated:
      self._errors.append('Source text appears untranslated. Translate it fully into the target language.')

  def _glossaryUntranslated(self):
    untranslated = glossary.untranslatedEntryes(self._translated)
    # print(self._cleaned_translated)
    if len(untranslated) > 0:
      self._errors.append(f'Untranslated terms found: {quoted_list(untranslated)}. Translate each specified term into the target language.')

  def _isAllowedChar(self, ch):
    if ch.isalpha():
      return False
    if ch.isdigit():
      return False
    if ch.isspace():
      return False
    if unicodedata.category(ch).startswith('P'):
      return False
    return True

  def _extraCharacters(self):
    chars_original   = set(''.join(ch for ch in self._cleaned_original   if self._isAllowedChar(ch)))
    chars_translated = set(''.join(ch for ch in self._cleaned_translated if self._isAllowedChar(ch)))
    extra_in_translated = chars_translated - chars_original
    if bool(extra_in_translated):
      self._errors.append(f'Translation contains extra characters not in the source: {quoted_list(extra_in_translated)}. Remove them and output only the faithful translation.')

  def errorsAsContext(self):
    return {
      'text': self._translated,
      'errors': self._errors
    }

  def errors(self):
    return self._errors

  def show(self):
    rprint(f'[bright_red]Errors in translation:[/bright_red]')
    for error in self._errors:
      rprint(f'    [red1]{escape(error.split('. ')[0])}[/red1]')
    table = Table(expand=True)
    table.add_column("Original"  ,  style="yellow", no_wrap=False, highlight=False)
    table.add_column("Translated",  style="green" , no_wrap=False, highlight=False)
    table.add_row(escape(self._original), escape(self._translated))
    Console().print(table)


  def check(self):
    self._answerIsEmpty()
    self._tagsDifferent()
    self._placeholdersDifferent()
    self._anchorsDifferent()
    if len(self._cleaned_original) > 4:
      if not glossary.isGlossaryPhrase(self._cleaned_translated):
        self._tooManyUntranslated()
        self._fullyUntranslated()
      self._answerTooLong()
    self._extraCharacters()
    self._glossaryUntranslated()
    return len(self._errors) == 0
