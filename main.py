from empyrion.translation import translation
# from empyrion.definition import definition
from empyrion.arguments import CArguments
from empyrion.graph import CGraph

# from empyrion.options import options

import pprint

def main():
  args = CArguments()
  if args.isTranslation():
      print("Translation mode enabled")
      translation.translate()
  if args.isGraph():
      print("Graph mode enabled")
      graph = CGraph()
      graph.construct()

if __name__ == "__main__":
  main()
