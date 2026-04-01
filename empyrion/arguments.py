import argparse

class CArguments:
  def __init__(self):
    self._parser = argparse.ArgumentParser(description='Empyrion RE2 Tools')
    self._parser.add_argument('--translation', action='store_true', help='Enable translation mode')
    self._parser.add_argument('--rmduplicates', action='store_true', help='Remove translation duplicates data')
    self._parser.add_argument('--graph', action='store_true', help='Enable graph mode')
    self._args = self._parser.parse_args()

  def isTranslation(self):
    return self._args.translation

  def isGraph(self):
    return self._args.graph

  def isRemoveTranslationDuplicates(self):
    return self._args.rmduplicates
