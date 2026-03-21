from empyrion.parsers.csv import CCsv
from empyrion.options import options
from empyrion.ollama import ollama

class CTranslation:
  def __init__(self, src_language, dst_language):
    self.localization = CCsv(options.get("conf_path", 'data') + "/Extras/Localization.csv"            , src_language, dst_language)
    self.dialogues    = CCsv(options.get("conf_path", 'data') + "/Content/Configuration/Dialogues.csv", src_language, dst_language)
    self.pda          = CCsv(options.get("conf_path", 'data') + "/Extras/PDA/PDA.csv"                 , src_language, dst_language)

  def _translate(self, what):
    for key in what.keys():
      src_text = what.get_src_language(key)
      print(f"{key}: {src_text}")
      translated = ollama.query(src_text)
      print(translated)

  def translate(self):
    self._translate(self.localization)
    # print(self.localization.keys())



translation = CTranslation(options.get("translation.src_language", "English"), options.get("translation.dst_language", "Russian"))
