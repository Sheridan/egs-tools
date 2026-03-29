from empyrion.parsers.csv import CCsv
from empyrion.options import options

import re

class CTranslation:
  def __init__(self, src_language, dst_language):
    self.data = {
      'localization': CCsv(options.get("conf_path", 'data') + "/Extras/Localization.csv"            , src_language, dst_language),
      'dialogues':    CCsv(options.get("conf_path", 'data') + "/Content/Configuration/Dialogues.csv", src_language, dst_language),
      'pda':          CCsv(options.get("conf_path", 'data') + "/Extras/PDA/PDA.csv"                 , src_language, dst_language),
    }

  def __getitem__(self, key):
    return self.data[key]

  def getLocalizationSrcLanguageText(self, key):
    if self.data['localization'].exists(key):
      text = self.data['localization'].get_src_language(key)
      return re.sub(r'\[.*?\]', '', text).replace('\\n', ' ')
    return None


  # def _translate(self, what):
  #   for key in what.keys():
  #     src_text = what.get_src_language(key)
  #     print(f"{key}: {src_text}")
  #     translated = ollama.query(src_text)
  #     print(translated)

  # def translate(self):
  #   self._translate(self.data['localization'])
  #   # print(self.localization.keys())


translation = CTranslation(options.get("translation.src_language", "English"), options.get("translation.dst_language", "Russian"))
