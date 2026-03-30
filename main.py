from empyrion.arguments import CArguments
from empyrion.graph import CGraph
from empyrion.translate.things import CTranslateThings
from empyrion.translate.dialogs import CTranslateDialogs
from empyrion.translate.pda import CTranslatePda

def main():
  args = CArguments()
  if args.isTranslation():
      print("Translation mode enabled")
      CTranslateThings().translate()
      CTranslateDialogs().translate()
      CTranslatePda().translate()

  if args.isGraph():
      print("Graph mode enabled")
      graph = CGraph()
      graph.construct()

if __name__ == "__main__":
  main()
