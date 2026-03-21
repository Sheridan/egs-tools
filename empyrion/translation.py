from empyrion.parsers.csv import CCsv

class CTranslation:
  def __init__(self, src_language_column, dst_language_column):
    self.localization = CCsv("data/Extras/Localization.csv"            , src_language_column, dst_language_column)
    self.dialogues    = CCsv("data/Content/Configuration/Dialogues.csv", src_language_column, dst_language_column)
    self.pda          = CCsv("data/Extras/PDA/PDA.csv"                 , src_language_column, dst_language_column)
