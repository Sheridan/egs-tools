import re
from difflib import SequenceMatcher
from empyrion.markup.tagsprocessor import tags_processor
from empyrion.markup.atanchorsprocessor import atanchors_processor
# def remove_tags(text):
#   text = re.sub(r'\[[a-zA-Z0-9-/]+?\]', '', text)
#   text = re.sub(r'<[a-zA-Z0-9#/]+?>', '', text)
#   return text

def clean_spaces(text):
  return ' '.join(text.split(' '))

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
  return atanchors_processor.removeAtAnchors(clean_spaces(remove_all_newlines(tags_processor.removeTags(text))))

def text_for_translate(text):
  return text.strip()

def text_for_graph_labels(text):
  return atanchors_processor.removeAtAnchors(clean_spaces(replace_literals_newlines_by_newlines(tags_processor.removeTags(text))))

def similarity_sequence(text1, text2):
  return SequenceMatcher(None, text1, text2).ratio() * 100

def rich_colorize_hex(s):
  return re.sub(r'([a-fA-F0-9]{6})', r'[#\1]\1[/]', s)

def no_letters(s: str) -> bool:
  return not any(ch.isalpha() for ch in s)

def estimate_tokens(text: str) -> str:
  if not text:
    return "[0:0]"
  n = len(text)
  min_tokens = max(1, n // 4)
  max_tokens = max(1, int(n / 1.5))
  return f"[{min_tokens}:{int((min_tokens+max_tokens)/2)}:{max_tokens}]"

def count_english_letters(text):
  return sum(1 for c in text if 'a' <= c <= 'z' or 'A' <= c <= 'Z')
