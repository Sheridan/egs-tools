import os
from empyrion.parsers.ecf import CEcf
from empyrion.options import options


import pprint

class CDefinition:
  def __init__(self):
    self.data = {
      'blockGroupsConfig':      CEcf(options.get("conf_path") + "/Content/Configuration/BlockGroupsConfig.ecf"     , "BlockGroup"           , "Name"),
      'blocksConfig':           CEcf(options.get("conf_path") + "/Content/Configuration/BlocksConfig.ecf"          , "Block"                , "Name"),
      'containers':             CEcf(options.get("conf_path") + "/Content/Configuration/Containers.ecf"            , "Container"            , "Id"),
      'damageMultiplierConfig': CEcf(options.get("conf_path") + "/Content/Configuration/DamageMultiplierConfig.ecf", "DamageMultiplierGroup", "Name"),
      'dialogues':              CEcf(options.get("conf_path") + "/Content/Configuration/Dialogues.ecf"             , "Dialogue"             , "Name"),
      'eClassConfig':           CEcf(options.get("conf_path") + "/Content/Configuration/EClassConfig.ecf"          , "Entity"               , "Name"),
      'eGroupsConfig':          CEcf(options.get("conf_path") + "/Content/Configuration/EGroupsConfig.ecf"         , "EGroup"               , "Name"),
      'factions':               CEcf(options.get("conf_path") + "/Content/Configuration/Factions.ecf"              , "Faction"              , "Name"),
      'galaxyConfig':           CEcf(options.get("conf_path") + "/Content/Configuration/GalaxyConfig.ecf"          , "GalaxyConfig"         , "Name"),
      'globalDefsConfig':       CEcf(options.get("conf_path") + "/Content/Configuration/GlobalDefsConfig.ecf"      , "GlobalDef"            , "Name"),
      'itemsConfig':            CEcf(options.get("conf_path") + "/Content/Configuration/ItemsConfig.ecf"           , "Item"                 , "Name"),
      'lootGroups':             CEcf(options.get("conf_path") + "/Content/Configuration/LootGroups.ecf"            , "LootGroup"            , "Name"),
      'materialConfig':         CEcf(options.get("conf_path") + "/Content/Configuration/MaterialConfig.ecf"        , "Material"             , "Name"),
      'statusEffects':          CEcf(options.get("conf_path") + "/Content/Configuration/StatusEffects.ecf"         , "StatusEffect"         , "Name"),
      'templates':              CEcf(options.get("conf_path") + "/Content/Configuration/Templates.ecf"             , "Template"             , "Name"),
      'tokenConfig':            CEcf(options.get("conf_path") + "/Content/Configuration/TokenConfig.ecf"           , "Token"                , "Id"),
      'traderNPCConfig':        CEcf(options.get("conf_path") + "/Content/Configuration/TraderNPCConfig.ecf"       , "Trader"               , "Name"),
    }

    # self.defReputation          = CEcf("data/Content/Configuration/DefReputation.ecf"         , "Reputation"           , "Name")
    # self.factionWarfare         = CEcf("data/Content/Configuration/FactionWarfare.ecf"        , "Element"              , "Name")

  def __getitem__(self, key):
    return self.data[key]




definition = CDefinition()
