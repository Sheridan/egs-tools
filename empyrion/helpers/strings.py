import re
from difflib import SequenceMatcher
from empyrion.helpers.tagsprocessor import tags_processor
# def remove_tags(text):
#   text = re.sub(r'\[[a-zA-Z0-9-/]+?\]', '', text)
#   text = re.sub(r'<[a-zA-Z0-9#/]+?>', '', text)
#   return text

def clean_spaces(text):
  return ' '.join(text.split(' '))

def remove_atanchor(text):
  return re.sub(r'@[a-z]+\d+', '', text, flags=re.IGNORECASE)

def remove_newlines(text):
  return text.replace('\n', ' ')

def remove_newlines_literals(text):
  return text.replace('\\n', ' ')

def replace_newlines_by_literals_newlines(text):
  return text.replace('\n', '\\n')

def replace_literals_newlines_by_newlines(text):
  return text.replace('\\n', '\n')

def remove_all_newlines(text):
  return remove_newlines(remove_newlines_literals(text))

def text_for_context(text):
  return remove_atanchor(clean_spaces(remove_all_newlines(tags_processor.removeTags(text))))

def text_for_translate(text):
  return text.strip()

def text_for_graph_labels(text):
  return remove_atanchor(clean_spaces(replace_literals_newlines_by_newlines(tags_processor.removeTags(text))))

def similarity_sequence(text1, text2):
  return SequenceMatcher(None, text1, text2).ratio() * 100

def rich_colorize_hex(s):
  return re.sub(r'([a-fA-F0-9]{6})', r'[#\1]\1[/]', s)

def is_atanchor_in_text(text):
  return bool(re.search(r'@[a-zA-Z][0-9]', text))

def no_letters(s: str) -> bool:
  return not any(ch.isalpha() for ch in s)
