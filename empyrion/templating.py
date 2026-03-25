from jinja2 import Template, Environment, FileSystemLoader

import re
import hashlib
import colorsys

from empyrion.model.things import things
from empyrion.translation import translation
from empyrion.options import options

def gen_color(text, lightness=0.75, saturation=0.7):
  """
  Генерирует светлый цвет для тёмной темы на основе строки.

  :param text: Исходная строка
  :param lightness: Светлота (0.7-0.9 для тёмной темы)
  :param saturation: Насыщенность (0.5-0.8 для приятных цветов)
  :return: Hex цвет без #
  """

  # Хеш строки для детерминированности
  hash_hex = hashlib.md5(text.encode()).hexdigest()

  # Hue (оттенок) из хеша - даёт разнообразие цветов
  hue = int(hash_hex[:8], 16) % 360 / 360

  # Конвертация HSL → RGB
  r, g, b = colorsys.hls_to_rgb(hue, lightness, saturation)

  # В hex формат
  return f'{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}'

def get_thing(key):
  return things.getThing(key)

def graphviz_escape(value):
    return (value
            .replace('&', '&amp;')
            .replace('<', '&lt;')
            .replace('>', '&gt;')
            .replace('"', '&quot;'))

def clean_node_name(name):
    # return re.sub(r"[\.x]")
    return re.sub('[^0-9a-z]+', '_', name.lower())

class CTemplating:
  def __init__(self):
    self.j2env = Environment(loader=FileSystemLoader('templates'))
    self.j2env.filters['gen_color'] = gen_color
    self.j2env.filters['get_thing'] = get_thing
    self.j2env.filters['graphviz_escape'] = graphviz_escape
    self.j2env.filters['clean_node_name'] = clean_node_name

  def loadTemplate(self, where, name):
    with open(f"templates/{where}/{name}.dot.j2", 'r', encoding='utf-8') as f:
      return self.j2env.from_string(f.read().strip())

  def cleanString(self, string):
     return '\n'.join(line for line in string.splitlines() if line.strip())

templating = CTemplating()
