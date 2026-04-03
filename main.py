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

def main():
  args = CArguments()
  if args.isTranslation():
      print("Translation mode enabled")
      translateThings()
      translatePda()
      translateDialogs()

      # from empyrion.model.dialogs import CDialogs
      # CDialogs().dialogs()

  if args.isGraph():
      print("Graph mode enabled")
      from empyrion.graph import CGraph
      graph = CGraph()
      graph.construct()

  if args.isRemoveTranslationDuplicates():
     from empyrion.state.state import state
     state.clearDuplicates()
     state.save()

if __name__ == "__main__":
  main()
