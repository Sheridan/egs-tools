import argparse

# Класс для парсинга опций командной строки

class CArguments:
  def __init__(self):
    self.parser = argparse.ArgumentParser(description='Empyrion RE2 Tools')
    self.parser.add_argument('--translation', action='store_true', help='Enable translation mode')
    self.parser.add_argument('--graph', action='store_true', help='Enable graph mode')
    self.args = self.parser.parse_args()

  def isTranslation(self):
    # return True if set 'translation' flag
    return self.args.translation

  def isGraph(self):
    # return True if set 'graph' flag
    return self.args.graph
