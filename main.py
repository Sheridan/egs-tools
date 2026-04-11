from empyrion.arguments import CArguments

def translateThings():
  from empyrion.translate.things import CTranslateThings
  CTranslateThings().translate()

def translateDialogs():
  from empyrion.translate.dialogs import CTranslateDialogs
  CTranslateDialogs().translate()

def translatePda():
  from empyrion.translate.pda import CTranslatePda
  CTranslatePda().translate()

def search(s, rm):
  if s is not None:
    from empyrion.translate.interface import CView
    CView().search(s, rm)

def stat():
  from empyrion.database.state import CStateDB
  from empyrion.database.stat import statistics
  CStateDB(None).showTranslateState()
  statistics.show()

def main():
  args = CArguments()
  if args.isStat():
    stat()

  if args.isTranslation():
    print("Translation mode enabled")
    translateDialogs()
    translatePda()
    translateThings()

  if args.isGraph():
    print("Graph mode enabled")
    from empyrion.graph import CGraph
    graph = CGraph()
    graph.construct()

  if args.isSearch():
    search(args.getOptionValue('search'), args.getOptionValue('rm'))

if __name__ == "__main__":
  main()
