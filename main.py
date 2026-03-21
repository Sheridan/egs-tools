from empyrion.translation import CTranslation
from empyrion.definition import CDefinition

import pprint

def main():
  translation = CTranslation(0, 8)
  print(translation.pda.get_src_language('pda_uqiiG'))
  print(translation.dialogues.get_src_language('dialogue_mqS04'))
  print(translation.localization.get_src_language('MushroomSpiky'))
  # translation.localization.saveAs('tmp_l.csv')

  definition = CDefinition()
  # print(definition.templates.names())

  # print(definition.blockGroupsConfig.names())
  # print(definition.blocksConfig.names())
  # print(definition.containers.names())
  # print(definition.damageMultiplierConfig.names())
  # print(definition.defReputation.names())
  print(definition.dialogues.names())
  # print(definition.eClassConfig.names())
  # print(definition.eGroupsConfig.names())
  # print(definition.factionWarfare.names())
  # print(definition.factions.names())
  # print(definition.galaxyConfig.names())
  # print(definition.globalDefsConfig.names())
  # print(definition.itemsConfig.names())
  # print(definition.lootGroups.names())
  # print(definition.materialConfig.names())
  # print(definition.statusEffects.names())
  # print(definition.templates.names())
  # print(definition.tokenConfig.names())
  # print(definition.traderNPCConfig.names())

  # pprint.pprint(definition.templates.get("Name", "FastRocket"), indent=2, width=160)
  # pprint.pprint(definition.itemsConfig.get("Name", "Eden_SurveyMiningT2"), indent=2, width=160)

if __name__ == "__main__":
  main()
