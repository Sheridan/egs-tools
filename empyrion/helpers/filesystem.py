import os

def ensure_folder_exists(f):
  os.makedirs(f, exist_ok=True)

def append_to_file(filename, s):
  ensure_folder_exists('trash')
  fn = f'trash/{filename}.log'
  if not s.endswith('\n'):
    s += '\n'
  with open(fn, 'a', encoding='utf-8') as lf:
    lf.write(s)
