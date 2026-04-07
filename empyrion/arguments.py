import argparse

class CArguments:
  def __init__(self):
    self._parser = argparse.ArgumentParser(description='Empyrion RE2 Tools')
    self._parser.add_argument('--translation', action='store_true', help='Enable translation mode')
    self._parser.add_argument('--rmduplicates', action='store_true', help='Remove translation duplicates data')
    self._parser.add_argument('--graph', action='store_true', help='Enable graph mode')

    self._parser.add_argument('--rm', action='store_true', help='Removes translation data from storages. Next run translate for new translation. Use with --show-key, --search')
    self._parser.add_argument('--show-key', dest='show', type=str, help='Show translation key record')
    self._parser.add_argument('--search', dest='search', type=str, help='Search text in translation')
    self._parser.add_argument('--list', dest='list', type=str, help='List translation files records')

    self._args = self._parser.parse_args()

  def isTranslation(self):
    return self._args.translation

  def isGraph(self):
    return self._args.graph

  def isRemoveTranslationDuplicates(self):
    return self._args.rmduplicates

  def isShow(self):
    return self._args.show is not None

  def isSearch(self):
    return self._args.search is not None

  def isList(self):
    return self._args.list is not None

  def getOptionValue(self, option_name):
    return getattr(self._args, option_name, None)
