import argparse

class CArguments:
  def __init__(self):
    self.parser = argparse.ArgumentParser(description='Empyrion RE2 Tools')
    self.parser.add_argument('--translation', action='store_true', help='Enable translation mode')
    self.parser.add_argument('--rmduplicates', action='store_true', help='Remove translation duplicates data')
    self.parser.add_argument('--graph', action='store_true', help='Enable graph mode')
    self.args = self.parser.parse_args()

  def isTranslation(self):
    return self.args.translation

  def isGraph(self):
    return self.args.graph

  def isRemoveTranslationDuplicates(self):
    return self.args.rmduplicates
