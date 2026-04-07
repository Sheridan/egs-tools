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

def showKey(key, rm):
  if key is not None:
    from empyrion.translate.interface import CView
    CView().showKey(key, rm)

def showList(name):
  if name is not None:
    from empyrion.translate.interface import CView
    CView().showList(name)

def search(s, rm):
  if s is not None:
    from empyrion.translate.interface import CView
    CView().search(s, rm)

def main():
  args = CArguments()
  if args.isTranslation():
    print("Translation mode enabled")
    translateThings()
    translateDialogs()
    translatePda()

  if args.isGraph():
    print("Graph mode enabled")
    from empyrion.graph import CGraph
    graph = CGraph()
    graph.construct()

  if args.isRemoveTranslationDuplicates():
    from empyrion.state.state import state
    state.clearDuplicates()
    state.save()

  if args.isShow():
    showKey(args.getOptionValue('show'), args.getOptionValue('rm'))

  if args.isList():
    showList(args.getOptionValue('list'))

  if args.isSearch():
    search(args.getOptionValue('search'), args.getOptionValue('rm'))

if __name__ == "__main__":
  main()
