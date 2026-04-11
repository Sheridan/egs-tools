import argparse

class CArguments:
  def __init__(self):
    self._parser = argparse.ArgumentParser(description='Empyrion RE2 Tools')
    self._parser.add_argument('--translation', action='store_true', help='Enable translation mode')
    self._parser.add_argument('--graph', action='store_true', help='Enable graph mode')

    self._parser.add_argument('--search', dest='search', type=str, help='Search text in translation')
    self._parser.add_argument('--rm', action='store_true', help='Removes translation data from storages. Next run translate for new translation. Use with --search')

    self._parser.add_argument('--stat', action='store_true', help='Show stored statistics')

    self._args = self._parser.parse_args()

  def isTranslation(self):
    return self._args.translation

  def isGraph(self):
    return self._args.graph

  def isStat(self):
    return self._args.stat

  def isSearch(self):
    return self._args.search is not None

  def getOptionValue(self, option_name):
    return getattr(self._args, option_name, None)
