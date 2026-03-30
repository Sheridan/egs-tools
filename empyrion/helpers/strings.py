import re

def remove_tags(text):
  text = re.sub(r'\[.*?\]', '', text)
  text = re.sub(r'<.*?>', '', text)
  return text

def clean_spaces(text):
  return ' '.join(text.split(' '))

def replace_name_brackets(text):
  return re.sub(r'\[([\s/a-zA-Z0-9-][^\]]*[^a-zA-Z0-9-])\]', r'|\1|', text)

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
  return remove_atanchor(clean_spaces(remove_all_newlines(remove_tags(replace_name_brackets(text)))))

def text_for_translate(text):
  return replace_name_brackets(text)

def text_for_graph_labels(text):
  return remove_atanchor(clean_spaces(replace_literals_newlines_by_newlines(remove_tags(replace_name_brackets(text)))))

def is_untranslated_string(text):
  tmp = text.strip()
  if tmp in ['===', '-', '====', '---', '...']:
    return True
  if re.fullmatch(r'\d+/\d+', tmp):
    return True
  return False
